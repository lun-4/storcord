# storcord

a badly-designed document store on top of discord (meme, not production ready, NOT PRODUCTION READY)

## testimonials

> Stor Corded is the futuer of the websc aled . Please help me im trapped in lun4s basement and theres no way out

- Not Nite

> Fuck you all

- Anonymous

> heroku delete my data base, storcord fix all my problem

- vivi

# install

```
python3 -m venv env
env/bin/pip install -Ur requirements.txt

cp config.example.yml config.yml
# edit config.yml with your token

# edit config/storcord.yml with the guild ids you want to use as backing
# store
```

# run

```
env STORCORD_AUTH_TOKEN=something_you_want_here python3 -m lifesaver.cli
```

then `stor!help`

# drawbacks

- its discord as a backing store. what the hell would you want with this
- max ~2kb documents lol (future work on document sharding is pending)

# le api

have `Authorization` header set to the value in `STORCORD_AUTH_TOKEN`

- `PUT /api/v1/GUILD_ID/collections/NAME` to create a collection
- `PUT /api/v1/GUILD_ID/collections/NAME/document` to create a document
- `PUT /api/v1/GUILD_ID/collections/NAME/find` to find a document
- `PUT /api/v1/GUILD_ID/collections/NAME/delete` to delete a document
