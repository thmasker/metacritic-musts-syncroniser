import os

import imdb_updater

list_id = os.environ.get('MUST_SEE_LIST_ID')
movie_url = "https://www.metacritic.com/browse/movie/all/all/metascore/"
imdb_updater.update_imdb_list(list_id, movie_url)
