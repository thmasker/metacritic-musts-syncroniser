# metacritic-musts-syncroniser
Tool that maintains Metacritic's Must See and Must Watch lists

# To generate imdb_profile folder

```shell
# 1. Create a fresh staging folder
mkdir -p imdb_profile

# 2. Copy only the essential session files from your Ubuntu Chrome
cp -r ~/.config/google-chrome/Default/Cookies* ./imdb_profile/
cp -r ~/.config/google-chrome/Default/Local\ Storage ./imdb_profile/
cp -r ~/.config/google-chrome/Default/Session\ Storage ./imdb_profile/
cp -r ~/.config/google-chrome/Default/Network ./imdb_profile/

# 3. Zip it up
zip -r imdb_profile.zip imdb_profile
```
