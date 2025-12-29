import csv
import datetime

import metacritic_scraper


def update_imdb_list(movie_url: str, input: str, output: str):
    metacritic_list = metacritic_scraper.get_metacritic_titles(movie_url)
    print(f"Found {len(metacritic_list)} items matching your criteria:")
    for m in metacritic_list:
        print(f"- {m['title']} ({m['year']}, {m['score']} score, {m['imdb_id']})")

    generate_csv_file(metacritic_list, input, output)


def reconcile_lists(metacritic_list, existing):
    existing_by_id = {d['Const']: d for d in existing}
    existing_by_name = {(d['Title'], str(d['Year'])): d for d in existing}
    metacritic_ids = {m['imdb_id'] for m in metacritic_list if m['imdb_id']}

    to_add = []
    to_remove = []
    to_update = []

    for m in metacritic_list:
        m_id = m['imdb_id']
        m_title = m['title']
        m_year = str(m['year'])
        m_score = str(m['score'])

        match = None
        if m_id and m_id in existing_by_id:
            match = existing_by_id[m_id]
        elif (m_title, m_year) in existing_by_name:
            match = existing_by_name[(m_title, m_year)]

        if not match:
            to_add.append(m)
        else:
            if str(match.get('Description')) != m_score:
                to_update.append(m)

    for e in existing:
        if e['Const'] not in metacritic_ids:
            to_remove.append(e)

    return to_add, to_remove, to_update


def write_to_file(items, file):
    for item in items:
        file.write(f"{item.get('imdb_id')}\t{item.get('year')}\t{item.get('title')}\t{item.get('score')}\n")


def generate_csv_file(metacritic_list, input: str, output: str):
    existing = None
    with open(input, "r") as file:
        existing = list(csv.DictReader(file))

    to_add, to_remove, to_update = reconcile_lists(metacritic_list, existing)
    with open(output, "w") as out:
        out.write(f"Updated on: {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}\n\n")
        out.write("Earned badge:\n\n")
        write_to_file(to_add, out)

        out.write("\nLost badge:\n\n")
        for item in to_remove:
            out.write(f"{item.get('Const')}\t{item.get('Year')}\t{item.get('Title')}\t{item.get('Description')}\n")

        out.write("\nUpdated Metascore:\n\n")
        write_to_file(to_update, out)
