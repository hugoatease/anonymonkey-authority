# anonymonkey-authority

Anonymonkey is an attempt at creating an anonymous survey mechanism.
Surveyors hosts their questions on a web service which allows users belonging
to a panel to answer anonymously.

This repository contains the survey authority web service used to negotiate
anonymous tokens and assert access to surveys on survey servers.

Please refer to [the anonymonkey repository](https://github.com/hugoatease/anonymonkey)
for more information about project features, and dependencies.

Configuration and setup
============
## Quick start

Anonymonkey is hosted on [anonymonkey.caille.me](http://anonymonkey.caille.me),
alongside with the authority service on `http://authority.caille.me`.

[The anonymonkey repository](https://github.com/hugoatease/anonymonkey)
contains a `docker-compose.yml` file useful to setup a development authority service
alongside with a sample survey service.

Anonymonkey service is exposed to the Docker host on port `8000`, and
authority service on port `8080`.

Email sending is handled by [Mailgun](http://www.mailgun.com/).
Mailgun allows to send emails reliably without the use of a SMTP server.

You need valid production or sandbox Mailgun credentials in order to send survey
sharing emails.

## Configuration reference
Anonymonkey service configuration is stored in the `settings.py` file.

Before going into production, you must change the sample settings by
providing values for the variables below.

| Parameter name                    | Description                |
|:----------------------------------|:---------------------------|
| `DEBUG`                           | Should the application be in debug mode. Set this to False in production |
| `MONGODB_DB`                      | MongoDB database name |
| `MONGODB_HOST` | MongoDB server hostname |
| `MONGODB_PORT` | MongoDB server port |
| `REDIS_HOST` | Redis server hostname |
| `REDIS_PORT` | Redis server port |
| `OPENID_CLIENT`                       | OpenID Connect OAuth client ID |
| `OPENID_ISSUER_KEY` | OpenID server public key used to sign JWT assertions |
| `OPENID_ISSUER_CLAIM` | JWT issuer claim of OpenID Connect server |
| `TOKEN_ISSUER` | JWT issuer used in survey access assertions tokens |
| `TOKEN_KEY` | Private RSA key used to sign JWTs |
| `TOKEN_KEY_PUBLIC` | Public RSA key used to sign JWTs |
| `MAIL_SENDER` | Email address to be used when sending emails |
| `MAILGUN_DOMAIN`                  | Mailgun registered domain name |
| `MAILGUN_KEY`                     | Mailgun sender API key |


### Manual setup
Python and Gunicorn are used to host the backend service. Node.js and Gulp are
required to compile static assets.

These commands assume you have active MongoDB and Redis server listening on
local host.

    git clone https://github.com/hugoatease/anonymonkey-authority.git
    cd anonymonkey-authority
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    pip install gunicorn
    npm install -g gulp
    npm install
    gulp
    gunicorn anonymonkey_authority:app

License
============
© 2016 Hugo Caille & Aymeric Masse.

Anonymonkey is released upon the terms of the Apache 2.0 License.
