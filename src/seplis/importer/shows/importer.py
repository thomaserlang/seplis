from seplis import schemas


def update_show(show):
    ''' Updates a show from the chosen importers.
    `show`
    '''

def show_info_changes(show_original, show_new):
    """Compares two show dicts for changes.
    If the return is an empty dict there is no
    difference between the two.

    :returns: dict
    """
    changes = {}
    skip_fields = (
        'externals',
        'indices',
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