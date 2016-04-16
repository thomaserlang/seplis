import logging
import requests, requests.exceptions
import time
from retrying import retry
from seplis import schemas, Client, config, constants, API_error
from .base import importers

logging.getLogger("requests").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
client = Client(
    url=config['client']['api_url'],
    access_token=config['client']['access_token'],
)

class Importer_upload_image_exception(Exception):
    pass

def update_show_by_id(show_id):
    show = client.get('/shows/{}'.format(show_id))
    if not show:
        logger.error('Unknown show: {}'.format(show_id))
        return 
    update_show(show)

def update_shows_all(from_show_id=1):
    shows = client.get('/shows', {
        'sort': 'id',
        'q': 'id:[{} TO *]'.format(from_show_id),
        'per_page': 500,
    })
    for show in shows.all():
        try:
            logging.info('Show: {}'.format(show['id']))
            update_show(show)
        except (
            KeyboardInterrupt, 
            SystemExit, 
            API_error, 
            Importer_upload_image_exception):
            raise
        except:
            logger.exception('update_shows_all')

def update_shows_incremental():
    logger.info('Incremental show update started')
    if not importers:
        logger.warn('No show importers registered')
    for key in importers:
        logger.info('Checking importer {}'.format(key))
        try:
            _importer_incremental(importers[key])
        except (
            KeyboardInterrupt, 
            SystemExit, 
            API_error, 
            Importer_upload_image_exception):
            raise
        except:
            logger.exception('_importer_incremental')

def _importer_incremental(importer):
    timestamp = time.time()    
    show_ids = _importer_incremental_updates_with_retry(importer)
    for show_id in show_ids:
        show = client.get('/shows/externals/{}/{}'.format(
            importer.external_name,
            show_id,
        ))
        if not show:
            continue
        logger.info('Found show "{}" by external {} {}'.format(
            show['id'],
            importer.external_name,
            show_id,
        ))
        if importer.external_name in show['importers'].values():
            update_show_with_retry(show)
        else:
            update_show_images(show)
    importer.save_timestamp(timestamp)

def _can_retry_update_show(exception):
    exceptions = (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.Timeout,
    )
    if type(exception) in exceptions:
        return True
    return False

@retry(
    stop_max_attempt_number=5,
    retry_on_exception=_can_retry_update_show,
    wrap_exception=False,
    wait_fixed=5000,
)
def _importer_incremental_updates_with_retry(importer):
    return importer.incremental_updates()

@retry(
    stop_max_attempt_number=5,
    retry_on_exception=_can_retry_update_show,
    wrap_exception=False,
    wait_fixed=5000,
)
def update_show_with_retry(show):
    return update_show(show)

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
        show = update_show_info(show)
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
        logging.info('Updating show "{}" info'.format(show['id']))
        show = client.patch(
            '/shows/{}'.format(show['id']), 
            info,
            timeout=120,
        )
    return show

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
        logging.info('Updating show "{}" episodes'.format(show['id']))
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
    images_added = []
    for name in imp_names:
        try:
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
                    images_added.append(
                        _save_image(show['id'], image)
                    )
                else:
                    i = image_external_ids[key]
                    if not i['hash']:
                        _upload_image(show['id'], i)
        except Importer_upload_image_exception:
            raise
        except:
            logging.exception('update_show_images')
    if (('poster_image' in show) and not show['poster_image']):
        _set_latest_image_as_primary(
            show['id'],
            image_id=images_added[-1]['id'] if images_added else None,
        )

def _save_image(show_id, image):
    saved_image = client.post(
        '/shows/{}/images'.format(show_id), 
        image
    )
    _upload_image(show_id, saved_image)
    return saved_image

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
        raise Importer_upload_image_exception(
            'Failed to upload data for image {}. '
            'Status code: {}. Error: {}'.format(
                image['id'],
                r.status_code,
                r.text,
            )
        )
    logging.info('Show "{}" new image uploaded: {}'.format(
        show_id,
        image['id'],
    ))
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

def _set_latest_image_as_primary(show_id, image_id=None):
    """Set the shows latests added image as the primary.
    If `image_id` is not None it will use the image id as
    the primary.
    """
    if not image_id:
        images = client.get('/shows/{}/images'.format(show_id), {
            'per_page': 1,
            'q': 'type:{} AND _exists_:hash'.format(
                constants.IMAGE_TYPE_POSTER
            ),
            'sort': 'created_at:desc',
        })
        if images:
            logging.info('Show "{}" new primary image: {}'.format(
                show_id,
                images[0]['id'],
            ))
            image_id = images[0]['id']
    if image_id:
        client.patch('/shows/{}'.format(show_id), {
            'poster_image_id': image_id,
        })

def call_importer(external_name, method, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.error('Unknown importer with id "{}"'.format(external_name))
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