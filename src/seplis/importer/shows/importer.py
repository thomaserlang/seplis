import logging
from seplis.api import constants
from seplis.config import config
from seplis import Client, schemas, API_error

def show_info_changes(show, show_new):
    changes = {}
    skip_fields = (
        'externals',
        'indices',
        'episodes',
    )
    for s in schemas._Show_schema:
        if not isinstance(s, str) or s in skip_fields:
            continue
        if s in show and s in show_new:
            if show[s] == None and isinstance(show_new[s], dict):
                continue
            if show[s] != show_new[s]:
                if isinstance(show[s], list):
                    changes[s] = list(set(show_new[s]) - set(show[s]))
                    if not changes[s]:
                        changes.pop(s)
                else:
                    changes[s] = show_new[s]
        elif s not in show and s in show_new:
            changes[s] = show_new[s]
    return changes

def show_episode_changes(episodes, episodes_new):
    changes = []
    current = {episode['number']: episode for episode in episodes}
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