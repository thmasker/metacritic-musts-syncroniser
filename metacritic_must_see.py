import imdb_updater

movie_url = 'https://www.metacritic.com/browse/movie/all/all/metascore/'
imdb_updater.update_imdb_list(movie_url, 'movies.csv', 'problematic-movies.json', 'movies-update.log')
