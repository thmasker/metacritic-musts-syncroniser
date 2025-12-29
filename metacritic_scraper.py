import requests
from bs4 import BeautifulSoup

import omdb_api

# Metacritic blocks basic scripts; we must pretend to be a real browser
headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}


def get_metacritic_titles(base_url: str):
    results = []
    current_page = 1
    keep_looking = True  # Will be false when Metascore reaches 80-

    while keep_looking:
        # Construct URL with pagination parameter
        url = f"{base_url}?page={current_page}"
        print(f"Scraping page {current_page}...")

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {current_page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # We look for the movie/show containers
        items = soup.find_all('div', class_='c-finderProductCard')

        if not items:
            print(f"No items found in page {current_page}")
            break

        for item in items:
            # 1. Extract Title
            title_tag = item.find('div', class_='c-finderProductCard_title')
            title = None
            if title_tag:
                spans = title_tag.find_all('span')
                title = spans[-1].get_text(strip=True)

            if not title:
                print(f"No title found for item in page {current_page}")
                break

            # 2. Extract Metascore
            score_tag = item.find('div', class_='c-siteReviewScore')
            score = int(score_tag.get_text(strip=True)) if score_tag else 0

            if score < 81:
                print(f"First movie with score < 81 found: {title}")
                keep_looking = False
                break

            # 3. Extract Must See/Watch badge
            must_image = item.find('img', class_='c-finderProductCard_mustImage')

            meta = item.find('div', class_='c-finderProductCard_meta')
            year = None
            if meta:
                spans = meta.find_all('span')
                if spans:
                    year = spans[0].get_text(strip=True)[-4:]

            # Filter based on Score 81+ and Must See/Watch badge
            if must_image and score >= 81:
                # 4. Get IMDb ID
                imdb_id = omdb_api.get_imdb_id(title, year)
                results.append({'title': title, 'year': year, 'score': score, 'imdb_id': imdb_id})

        current_page += 1

    # Remove duplicates based on title
    return {res['title']: res for res in results}.values()
