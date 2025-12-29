import imdb_updater

movie_url = "https://www.metacritic.com/browse/tv/all/all/metascore/"
imdb_updater.update_imdb_list(movie_url, "series.csv", "series-update.log")
