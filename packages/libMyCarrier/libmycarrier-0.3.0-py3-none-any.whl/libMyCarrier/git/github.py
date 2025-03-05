import time
import requests
import json
from jwt import JWT, jwk_from_pem

class githubAuth:
    """
    Class for authenticating and retrieving auth token from GitHub.

    Args:
        private_key_pem (str): Private Key PEM for GitHub authentication
        app_id (str): GitHub App id
        installation_id (str): GitHub App installation id

    Methods:
        get_auth_token: Get auth token from GitHub for the GitHub App

    Examples:
        # Get auth token from GitHub
        github_auth = githubAuth(private_key_pem, app_id, installation_id)
        
        # The returned token could be used with PyGithub API: https://github.com/PyGithub/PyGithub/tree/main/doc/examples
        g = Github(login_or_token=github_auth.token)
        org = g.get_organization("ORGNAME")
        repo = org.get_repo("REPONAME")
        
    """
    def __init__ (self, private_key_pem: str, app_id: str, installation_id: str):
        self.installation_id = installation_id
        self.signing_key = jwk_from_pem(str.encode(private_key_pem))

        self.payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's identifier
            'iss': app_id
        }

        self.jwt_instance = JWT()
        self.token = self.get_auth_token()

    def get_auth_token(self):
        try:
            encoded_jwt = self.jwt_instance.encode(self.payload, self.signing_key, alg='RS256')
            # Set Headers
            headers = {"Authorization": "Bearer {}".format(encoded_jwt),
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28" }
            # Get Access Token
            resp = requests.post('https://api.github.com/app/installations/{}/access_tokens'.format(self.installation_id), headers=headers)
            token = json.loads(resp.content.decode())['token']
            return token
        except Exception as error:
            raise error
