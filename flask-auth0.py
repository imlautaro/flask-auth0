import json

from six.moves.urllib.request import urlopen
from functools import wraps
from jose import jwt
from flask import jsonify, request, _request_ctx_stack


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Main class
class Auth0:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.load_config()
        self.load_error_handler()

    def load_config(self):
        self.DOMAIN = self.app.config['AUTH0_DOMAIN']
        self.AUDIENCE = self.app.config['AUTH0_AUDIENCE']

    def load_error_handler(self):
        @self.app.errorhandler(AuthError)
        def handle_auth_error(ex):
            response = jsonify(ex.error)
            response.status_code = ex.status_code
            return response

    def get_token_auth_header(self):
        # Get a token from the Authorization header.
        auth = request.headers.get("Authorization", None)
        if not auth:
            raise AuthError({
                "code": "authorization_header_missing",
                "description": "Authorization header is expected"
            }, 401)
        parts = auth.split()
        if parts[0].lower() != "bearer":
            raise AuthError({
                "code": "invalid_header",
                "description": "Authorization header must start with Bearer"
            }, 401)
        elif len(parts) == 1:
            raise AuthError({
                "code": "invalid_header",
                "description": "Token not found"
            }, 401)
        elif len(parts) > 2:
            raise AuthError({
                "code": "invalid_header",
                "description": "Authorization header must be Bearer token"
            }, 401)
        token = parts[1]
        return token

    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = self.get_token_auth_header()
            jsonurl = urlopen(f'https://{self.DOMAIN}/.well-known/jwks.json')
            jwks = json.loads(jsonurl.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=['RS256'],
                        audience=self.AUDIENCE,
                        issuer=f'https://{self.DOMAIN}/'
                    )
                except jwt.ExpiredSignatureError:
                    raise AuthError({
                        'code': 'invalid_claims',
                        'description': 'incorrect claims, please check the audience and issuer'
                    }, 401)
                except Exception:
                    raise AuthError({
                        'code': 'invalid_header',
                        'description': 'Unable to parse authentication token'
                    }, 401)
                _request_ctx_stack.top.current_user = payload
                return f(*args, **kwargs)
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find appropriate key'
            }, 401)
        return decorated

    def requires_scope(self, required_scope):
        token = self.get_token_auth_header()
        unverified_claims = jwt.get_unverified_claims(token)
        if unverified_claims.get('scope'):
            token_scopes = unverified_claims['scope'].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
        return False
