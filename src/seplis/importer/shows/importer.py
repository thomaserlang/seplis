import logging
import requests
from seplis import schemas, Client, config, constants
from .base import importers

logger = logging.getLogger(__name__)
client = Client(
    url=config['client']['api_url'],
    access_token=config['client']['access_token'],
)

def update_show(show):
    """Updates a show from the chosen importers in `show["importers"]`.
    
    ``show`` must be a show dict. Required keys: id, importers

    """
    if not show['externals']:
        logger.warn('The show has no externals')
        return
    if not show['importers']:
        logger.warn('The specified show has no importers')
        return
    if show['importers']['info']:
        update_show_info(show)
    if show['importers']['episodes']:
        update_show_episodes(show)
    update_show_images(show)

def update_show_info(show):
    """Retrieves show info from the specified info importer
    and compares it with the current show to only update
    if there are any changes.

    ``show`` must be a show dict.

    """
    info = call_importer(
        external_name=show['importers']['info'],
        method='info',
        show_id=show['externals'][show['importers']['info']],
    )
    if not info:
        return
    info = _show_info_changes(show, info)
    if info:
        client.patch(
            '/shows/{}'.format(show['id']), 
            info,
            timeout=120,
        )

def update_show_episodes(show):
    """Retrieves show episodes from the specified episode
    importer and compares them to the show's current episodes
    to only update if there are any changes.

    ``show`` must be a show dict.

    """
    episodes = client.get(
        '/shows/{}/episodes?per_page=500'.format(show['id'])
    ).all()

    imp_episodes = call_importer(
        external_name=show['importers']['episodes'],
        method='episodes',
        show_id=show['externals'][show['importers']['episodes']],
    )

    _cleanup_episodes(show['id'], episodes, imp_episodes)

    changes = _show_episode_changes(episodes, imp_episodes)
    if changes:
        client.patch(
            '/shows/{}'.format(show['id']),
            {'episodes': changes},
            timeout=120,
        )

def _cleanup_episodes(show_id, episodes, imported_episodes):
    """Sends an API request to delete episodes that 
    does not exist in `imported_episodes`

    ``episodes`` list of all the show's current episodes.

    ``imported_episodes`` list of all episodes imported from
        an external source.

    """
    imp_ep_numbers = [e['number'] for e in imported_episodes]
    for e in episodes:
        if e['number'] not in imp_ep_numbers:
            client.delete('/shows/{}/episodes/{}'.format(
                show_id, 
                e['number'],
            ))

def update_show_images(show):
    """Retrieves images from importers that support image import 
    and the external name is assigned to the show with an id.

    ``show`` must be a show dict.

    """
    imp_names = _importers_with_support(show['externals'], 'images')
    images = client.get(
        '/shows/{}/images?per_page=500'.format(show['id'])
    ).all()
    image_external_ids = {
        '{}-{}'.format(i['external_name'], i['external_id']): i
        for i in images
    }
    for name in imp_names:
        imp_images = call_importer(
            external_name=name, 
            method='images',
            show_id=show['externals'][name],
        )
        if not imp_images:
            continue
        for image in imp_images:
            key = '{}-{}'.format(image['external_name'], image['external_id'])
            if key not in image_external_ids:
                _save_image(show['id'], image)
            else:
                i = image_external_ids[key]
                if not i['hash']:
                    _upload_image(show['id'], i)
    if not show['poster_image_id']:
        _set_latest_image_as_primary(show['id'])

def _save_image(show_id, image):
    saved_image = client.post(
        '/shows/{}/images'.format(show_id), 
        image
    )
    _upload_image(show_id, saved_image)

def _upload_image(show_id, image):
    """Uploads the image specified in `image['source_url']`
    to the API server as saves it for `image`.

    ``image`` image dict.

    :returns: bool
    """
    if not image['source_url']:
        raise Exception('the image must contain a source URL')
    r = requests.get(image['source_url'], stream=True)
    if r.status_code != 200:
        raise Exception(
            'Could not retrieve the source image from "{}". Status code:'.format(
                image['source_url'],
                r.status_code,
            )
        )
    r = requests.put(
        client.url+'/shows/{}/images/{}/data'.format(show_id, image['id']),
        files={
            'image': r.raw,
        },
        headers={
            'Authorization': 'Bearer {}'.format(client.access_token),
        }
    )
    if r.status_code != 200:
        raise Exception(
            'Failed to upload data for image {}. '
            'Status code: {}. Error: {}'.format(
                image['id'],
                r.status_code,
                r.text,
            )
        )
    return True

def _importers_with_support(show_externals, support):
    """
    :returns: list of str
    """
    imp_names = []
    for name in importers:
        if name not in show_externals:
            continue
        if support in importers[name].supported:
            imp_names.append(name)
    return imp_names

def _set_latest_image_as_primary(show_id):
    images = client.get('/shows/{}/images'.format(show_id), {
        'per_page': 1,
        'q': 'type:{} AND _exists_:hash'.format(
            constants.IMAGE_TYPE_POSTER
        ),
        'sort': 'created_at:desc',
    })
    if images:
        client.patch('/shows/{}'.format(show_id), {
            'poster_image_id': images[0]['id'],
        })

def call_importer(external_name, method, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logging.error('Unknown importer with id "{}"'.format(external_name))
        return
    m = getattr(im, method, None)
    if not m:
        raise Exception('Unknown method "{}" for importer "{}"'.format(
            method,
            external_name
        ))
    return m(*args, **kwargs)

def _show_info_changes(show_original, show_new):
    """Compares two show dicts for changes.
    If the return is an empty dict there is no
    difference between the two.

    :returns: dict
    """
    changes = {}
    skip_fields = (
        'externals',
        'importers',
        'episodes',
    )
    for s in schemas._Show_schema:
        if not isinstance(s, str) or s in skip_fields:
            continue
        if s in show_original and s in show_new:
            if show_original[s] == None and isinstance(show_new[s], dict):
                continue
            if show_original[s] != show_new[s]:
                if isinstance(show_original[s], list):
                    changes[s] = list(set(show_new[s]) - set(show_original[s]))
                    if not changes[s]:
                        changes.pop(s)
                else:
                    changes[s] = show_new[s]
        elif s not in show_original and s in show_new:
            changes[s] = show_new[s]
    return changes


def _show_episode_changes(episodes_original, episodes_new):
    """Compares two episode list of dicts for changes.
    If the return is an empty list there is no
    difference between the two.

    :returns: list of dict
    """
    changes = []
    current = {episode['number']: episode for episode in episodes_original}
    for episode in episodes_new:
        data = {}
        current_episode = current[episode['number']] if episode['number'] in current else episode 
        if episode['number'] not in current:
            changes.append(episode)
            continue
        for s in schemas._Episode_schema:
            s = str(s)
            if s == 'number':
                data[s] = episode[s]
                continue
            if s in episode and s in current_episode:
                if episode[s] == None and isinstance(current_episode[s], dict):
                    continue
                if episode[s] != current_episode[s]:
                    data[s] = episode[s]
            elif s not in current_episode and s in episode:
                data[s] = episode[s]
        if data != {} and len(data) > 1:
            changes.append(data)
    return changes