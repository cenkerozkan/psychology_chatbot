import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin.auth import *

import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConnector:
    def __init__(self):
        self._cred: credentials.Certificate = credentials.Certificate(
            {
                "type": os.getenv("TYPE"),
                "project_id": os.getenv("PROJECT_ID"),
                "private_key_id": os.getenv("PRIVATE_KEY_ID"),
                "private_key": os.getenv("PRIVATE_KEY").replace(r'\n', '\n'),
                "client_email": os.getenv("CLIENT_EMAIL"),
                "client_id": os.getenv("CLIENT_ID"),
                "auth_uri": os.getenv("AUTH_URI"),
                "token_uri": os.getenv("TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
                "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
            }
        )
        self._api_key: str = os.getenv("WEB_API_KEY")
        self.app: firebase_admin = firebase_admin.initialize_app(self._cred)

    def get_firebase_app(self):
        return self.app

firebase_connector = FirebaseConnector().get_firebase_app()