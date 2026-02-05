import os

import requests


def get_imdb_id(title: str, year: str | None) -> str | None:
    """Fetches the IMDb ID for a given title using OMDb API"""
    omdb_api_key = os.environ.get('OMDB_API_KEY')
    params = {'t': title, 'y': year, 'apikey': omdb_api_key}
    response = requests.get('http://www.omdbapi.com/', params=params)
    data = response.json()

    if data.get('Response') == 'True':
        return data.get('imdbID')
    return None
