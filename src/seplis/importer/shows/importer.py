import logging
from seplis import schemas, Client, config
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
    if not show['importers']:
        return
    if show['importers']['info']:
        update_show_info(show)
    if show['importers']['episodes']:
        episodes = importer(
            id_=show['importers']['episodes'],
            method='episodes',
            show_id=show['id'],
        )
        if episodes:
            episodes = show_episode_changes(show['episodes'], episodes)
    if show['importers']['images']:
        images = importer(
            id_=show['importers']['images'],
            method='episodes',
            show_id=show['id'],
        )

def update_show_info(show):
    """Retrieves show info from the specified info importer
    and compares it with the current show to only update
    if there are any changes.

    ``show`` must be a show dict.

    """
    info = call_importer(
        id_=show['importers']['info'],
        method='info',
        show_id=show['id'],
    )
    if not info:
        return
    info = show_info_changes(show, info)
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
    ).all() or []

    imp_episodes = call_importer(
        id_=show['importers']['episodes'],
        method='episodes',
        show_id=show['id'],
    )

    cleanup_episodes(show['id'], episodes, imp_episodes)

    changes = show_episode_changes(episodes, imp_episodes)
    if changes:
        client.patch(
            '/shows/{}'.format(show['id']),
            {'episodes': changes},
            timeout=120,
        )

def cleanup_episodes(show_id, episodes, imported_episodes):
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

def call_importer(id_, method, *args, **kwargs):
    """Calls a method in a registered importer"""
    im = importers.get(id_)
    if not im:
        logging.error('Unknown importer with id "{}"'.format(id_))
        return
    m = getattr(im, method, None)
    if not m:
        raise Exception('Unknown method "{}" for importer "{}"'.format(
            method,
            id_
        ))
    return m(*args, **kwargs)

def show_info_changes(show_original, show_new):
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


def show_episode_changes(episodes_original, episodes_new):
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