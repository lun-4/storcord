# storcord

a badly-designed document store on top of discord (meme, not production ready, NOT PRODUCTION READY)

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
python3 -m lifesaver.cli
```

then `stor!help`

## drawbacks

- its discord as a backing store. what the hell would you want with this
- max ~2kb documents lol (future work on document sharding is pending)
