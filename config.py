# Evgeny Ovsov

'''
Configuration mostly contain credential for various services.
All logins and other public information placed here.
All passwords and other private information must be defined as system environment variables.
'''

import os

SMTP = {
    "login": "My.Email@gmail.com",
    "password": os.environ.get("SMTP_PASS"),
    "provider": "smtp.gmail.com"
}

MONGO = {
    "address": "127.0.0.1",
    "port": 27017,
    "base": "Clients",
    "collection": "Downloaders"
}

DIGITALOCEAN = {
    "key": os.environ.get("DIGOC_KEY"),
    "secret": os.environ.get("DIGOC_SECRET"),
    "endpoint": "https://sfo2.digitaloceanspaces.com",
    "region": "sfo2",
    "bucket": "???", # Digital Ocean spaces name
    "link_lifespan": 3600
}

SSL = {
    "cert": r"/etc/letsencrypt/live/mysite.com/fullchain.pem",
    "key": r"/etc/letsencrypt/live/mysite.com/privkey.pem"
}

FILES_MAP = {  # real filenames disguised by hashes
    "c05fbf4fea5db3648bc1634acc3668bd": "funny_dog.mkv"
}
