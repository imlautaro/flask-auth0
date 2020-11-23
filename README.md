# Flask-Auth0

An easy way to protect your API with Auth0

## Installation

`pip install git+https://github.com/imlautaro/flask-auth0.git#egg=flask_auth0`

## Usage

```python
from flask import Flask
from flask_auth0 import Auth0


app = Flask(__name__)

# Configuration required
app.config['AUTH0_DOMAIN'] = 'Your app domain'
app.config['AUTH0_AUDIENCE'] = 'Your audience API'

auth0 = Auth0(app)

@app.route('/public')
def public():
    return 'Hello world from public!'

@app.route('/protected')
@auth0.requires_auth
def protected():
    return 'Hello world from protected!'

@app.route('/protected-with-scope')
@auth0.requires_auth
def protected_with_scope():
    if auth0.requires_scope('read:messages'):
        return 'Hello world from protected with scope!'
    return "You don't have permission to see this"

if __name__ == '__main__':
    app.run()

```

You can also use `init_app` to initialize the app.
