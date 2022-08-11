import requests, requests.exceptions
import time
from retrying import retry
from seplis import schemas, Client, config, constants, API_error, logger
from .base import importers

client = Client(
    url=config.data.client.api_url,
    access_token=config.data.client.access_token,
)

class Importer_exception(Exception):
    pass

class Importer_upload_image_exception(Importer_exception):
    pass

def update_show_by_id(series_id):
    show = client.get('/shows/{}'.format(series_id))
    if not show:
        logger.error('Unknown show: {}'.format(series_id))
        return 
    update_show(show)

def update_shows_all(from_series_id=0, do_async=False):
    shows = client.get('/shows', {
        'per_page': 500,
        'from_id': from_series_id,
    })
    for show in shows.all():
        try:
            logger.info('Show: {}'.format(show['id']))
            if do_async:
                client.post('/shows/{}/update'.format(show['id']))
            else:
                update_show(show)
        except (
            KeyboardInterrupt, 
            SystemExit):
            raise
        except Exception as e:
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
            SystemExit):
            raise
        except Exception as e:
            logger.exception('update_shows_incremental')

def _importer_incremental(importer):
    timestamp = time.time()    
    series_ids = _importer_incremental_updates_with_retry(importer) or []
    for series_id in series_ids:
        show = client.get('/shows/externals/{}/{}'.format(
            importer.external_name,
            series_id,
        ))
        if not show:
            continue
        try:
            if importer.external_name in show['importers'].values():
                update_show_with_retry(show)
            else:
                update_show_images(show)
        except API_error:
            logger.exception('incremental show update')
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
        series_id=show['externals'][show['importers']['info']],
    )
    if not info:
        return show
    info = _show_info_changes(show, info)
    if info:
        logger.info('Updating show "{}" info'.format(show['id']))
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
    episodes = list(client.get(
        '/shows/{}/episodes?per_page=500'.format(show['id'])
    ).all())

    imp_episodes = call_importer(
        external_name=show['importers']['episodes'],
        method='episodes',
        series_id=show['externals'][show['importers']['episodes']],
    )
    if imp_episodes == None:
        return

    _cleanup_episodes(show['id'], episodes, imp_episodes)
    changes = _show_episode_changes(episodes, imp_episodes)

    if changes:
        logger.info('Updating show "{}" episodes'.format(show['id']))
        client.patch(
            '/shows/{}'.format(show['id']),
            {'episodes': changes},
            timeout=120,
        )

def _cleanup_episodes(series_id, episodes, imported_episodes):
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
                series_id, 
                e['number'],
            ))

def update_show_images(show):
    """Retrieves images from importers that support image import 
    and the external name is assigned to the show with an id.

    ``show`` must be a show dict.

    """
    if (('poster_image' in show) and show['poster_image']):
        # Need a better way to only download images in the 
        # correct size from THETVDB.
        # Right now a lot of time and bandwidth is spent redownloading
        # the same images just to find out that they are not 680x1000...
        # So for now only get the images if there is no poster set for the show.
        return
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
                series_id=show['externals'][name],
            )
            if not imp_images:
                continue
            for image in imp_images:
                key = '{}-{}'.format(image['external_name'], image['external_id'])
                if key not in image_external_ids:
                    si = _save_image(show['id'], image)
                    if si:
                        images_added.append(si)
                else:
                    i = image_external_ids[key]
                    if not i['hash']:
                        _upload_image(show['id'], i)
        except Importer_upload_image_exception:
            raise
        except:
            logger.exception('update_show_images')
    if (('poster_image' in show) and not show['poster_image']):
        _set_latest_image_as_primary(
            show['id'],
            image_id=images_added[0]['id'] if images_added else None,
        )

def _save_image(series_id, image):
    saved_image = client.post(
        '/shows/{}/images'.format(series_id), 
        image
    )
    if _upload_image(series_id, saved_image):
        return saved_image

def _upload_image(series_id, image):
    """Uploads the image specified in `image['source_url']`
    to the API server as saves it for `image`.

    ``image`` image dict.

    :returns: bool
    """
    if not image['source_url']:
        raise Exception('the image must contain a source URL')
    r = requests.get(image['source_url'], stream=True)
    if r.status_code != 200:
        # Delete the image from the database if the image could not 
        # be downloaded
        client.delete('/shows/{}/images/{}'.format(series_id, image['id']))
        raise Importer_exception(
            'Could not retrieve the source image from "{}". Status code: {}'.format(
                image['source_url'],
                r.status_code,
            )
        )
    r = requests.put(
        client.url+'/shows/{}/images/{}/data'.format(series_id, image['id']),
        files={
            image['source_url'][image['source_url'].rfind("/")+1:]: r.raw,
        },
        headers={
            'Authorization': 'Bearer {}'.format(client.access_token),
        }
    )
    if r.status_code != 200:
        # Delete the image from the database if the image could not 
        # be uploaded        
        client.delete('/shows/{}/images/{}'.format(series_id, image['id']))
        data = r.json()
        if data['code'] in (2004, 2101):
            logger.warning(
                data['message']+'\n\n'+image['source_url']
            )
            return False
        raise Importer_upload_image_exception(
            'Failed to upload data for image {}. '
            'Status code: {}. Error: {}'.format(
                image['id'],
                r.status_code,
                r.text,
            )
        )
    logger.info('Show "{}" new image uploaded: {}'.format(
        series_id,
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

def _set_latest_image_as_primary(series_id, image_id=None):
    """Set the shows latests added image as the primary.
    If `image_id` is not None it will use the image id as
    the primary.
    """
    if not image_id:
        images = client.get('/shows/{}/images'.format(series_id), {
            'per_page': 1,
            'q': 'type:{} AND _exists_:hash'.format(
                constants.IMAGE_TYPE_POSTER
            ),
            'sort': 'created_at:desc',
        })
        if images:
            logger.info('Show "{}" new primary image: {}'.format(
                series_id,
                images[0]['id'],
            ))
            image_id = images[0]['id']
    if image_id:
        client.patch('/shows/{}'.format(series_id), {
            'poster_image_id': image_id,
        })

def call_importer(external_name, method, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(external_name)
    if not im:
        logger.warn(
            'Show "{}" has an unknown importer at {} ' 
            'with external name "{}"'.format(
                kwargs.get('series_id'),
                method,
                external_name,
            )
        )
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