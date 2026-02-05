import csv
import datetime
import json

import metacritic_scraper


def update_imdb_list(movie_url: str, input: str, problematic_input: str, output: str):
    metacritic_list = metacritic_scraper.get_metacritic_titles(movie_url)
    print(f'Found {len(metacritic_list)} items matching your criteria:')
    for m in metacritic_list:
        print(f'- {m['title']} ({m['year']}, {m['score']} score, {m['imdb_id']})')

    generate_csv_file(metacritic_list, input, problematic_input, output)


def get_existing_lists(existing):
    existing_by_id, existing_by_name = {}, {}
    for e in existing:
        existing_by_id[e['Const']] = e
        existing_by_name[e['Title'].lower()] = e

    return existing_by_id, existing_by_name


def get_metacritic_lists(metacritic_list):
    metacritic_ids, metacritic_titles = [], []
    for m in metacritic_list:
        if m['imdb_id']:
            metacritic_ids.append(m['imdb_id'])
        if m['title']:
            metacritic_titles.append(m['title'])

    return metacritic_ids, metacritic_titles


def get_problematic_lists(problematic):
    problematic_imdb, problematic_metacritic = [], {}
    for p in problematic:
        problematic_imdb.append(p['imdb'])
        problematic_metacritic[p['metacritic']] = p['id']

    return problematic_imdb, problematic_metacritic


def reconcile_lists(metacritic_list, existing, problematic):
    existing_by_id, existing_by_name = get_existing_lists(existing)
    metacritic_ids, metacritic_titles = get_metacritic_lists(metacritic_list)
    problematic_imdb, problematic_metacritic = get_problematic_lists(problematic)

    to_add = []
    to_remove = []
    to_update = []

    for m in metacritic_list:
        m_id = m['imdb_id']
        m_title = m['title']
        m_score = str(m['score'])

        match = None
        if m_id and m_id in existing_by_id:
            match = existing_by_id[m_id]
        elif m_title in existing_by_name:
            match = existing_by_name[m_title]
        elif m_title in problematic_metacritic:
            match = existing_by_id[problematic_metacritic[m_title]]

        if not match:
            to_add.append(m)
        else:
            if str(match.get('Description')) != m_score:
                to_update.append(m)

    for e in existing:
        if (e['Const'] not in metacritic_ids and e['Title'].lower() not in metacritic_titles
                and e['Title'] not in problematic_imdb):
            to_remove.append(e)

    return to_add, to_remove, to_update


def write_to_file(items, file):
    for item in items:
        file.write(f'{item.get('imdb_id')}\t{item.get('year')}\t{item.get('title')}\t{item.get('score')}\n')


def generate_csv_file(metacritic_list, input: str, problematic_input: str, output: str):
    existing = None
    with open(input, 'r') as file:
        existing = list(csv.DictReader(file))

    with open(problematic_input, 'r') as file:
        problematic = json.load(file)

    to_add, to_remove, to_update = reconcile_lists(metacritic_list, existing, problematic)
    with open(output, 'w') as out:
        out.write(f'Updated on: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n')
        out.write('Earned badge:\n\n')
        write_to_file(to_add, out)

        out.write('\nLost badge:\n\n')
        for item in to_remove:
            out.write(f'{item.get('Const')}\t{item.get('Year')}\t{item.get('Title')}\t{item.get('Description')}\n')

        out.write('\nUpdated Metascore:\n\n')
        write_to_file(to_update, out)
