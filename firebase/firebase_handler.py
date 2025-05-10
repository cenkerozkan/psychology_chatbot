"""
This is the class responsible from communicating
with the firebase authentication service.
"""
import time

import requests

from util.logger import get_logger
from db.firebase_connector import firebase_connector

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin.auth import *
import os
from dotenv import load_dotenv

load_dotenv()
FIREBASE_APP = firebase_connector

class FirebaseHandler:
    def __init__(
            self
    ):
        self._logger = get_logger(__name__)
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
        self._app = FIREBASE_APP
        self._api_key: str = os.getenv("WEB_API_KEY")

    def _post_request_executor(
            self,
            payload: dict,
            endpoint: str
    ) -> dict:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={self._api_key}",
            json=payload
        )
        return response.json()

    def get_user_info(
            self,
            email: str
    ) -> dict:
        user_details = auth.get_user_by_email(email, app=self._app)
        return {
            "userUid": user_details.uid,
            "email": user_details.email,
            "emailVerified": user_details.email_verified,
        }

    def login(
            self,
            email: str,
            password: str
    ) -> dict:
        response: dict = self._post_request_executor({"email": email, "password": password, "returnSecureToken": True}, "signInWithPassword")
        return response

    def logout(
            self,
            user_uid: str
    ) -> bool:
        auth.revoke_refresh_tokens(user_uid, app=self._app)
        return True

    def register(
            self,
            email: str,
            password: str
    ) -> dict:
        # NOTE: We can also get username for this method.
        response = self._post_request_executor({"email": email, "password": password, "returnSecureToken": True}, "signUp")

        return response

    def delete_unverified_email(
            self,
            email: str
    ) -> None:
        self._logger.info(f"Waiting for 5 minutes to delete unverified email: {email}")
        time.sleep(5)
        user: UserRecord = auth.get_user_by_email(email)
        if not user.email_verified:
            auth.delete_user(user.uid)

    def send_verification_email(
            self,
            user_uid: str
    ) -> dict:
        response = self._post_request_executor({"requestType": "VERIFY_EMAIL", "idToken": user_uid}, "sendOobCode")
        return response


    def validate_token(
            self,
            token: str
    ) -> bool:
        try:
            decoded_token = auth.verify_id_token(token)
            return True
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError):
            return False
        except Exception:
            return False

    def delete_user(
            self,
            user_uid: str
    ) -> bool:
        self._logger.info(f"Deleting user with user uid: {user_uid}")
        auth.delete_user(user_uid, app=self._app)
        return True

    def create_admin_user(
            self,
            email: str,
            password: str
    ) -> dict:
        result: dict ={
            "uid": "",
            "email": email,
            "password": password
        }
        # NOTE: I always expect this method to work
        #       correctly, and this will be called
        #       in a try block. So it is always returning True
        #       if there is no problem with the firebase
        #       project.
        new_admin_user = auth.create_user(
            email=email,
            email_verified=True,
            password=password,
            app=self._app
        )
        result.update({"uid": new_admin_user.uid})
        return result

    def create_driver_user(
            self,
            phone_number: str,
    ) -> dict:
        result: dict = {
            "uid": "",
            "phone_number": phone_number,
        }
        new_driver_user = auth.create_user(
            phone_number=phone_number,
            app=self._app
        )

        result.update({"uid": new_driver_user.uid, "phone_number": new_driver_user.phone_number})
        return result

    def remove_driver_user(
            self,
            user_uid: str
    ) -> bool:
        auth.delete_user(user_uid, app=self._app)
        return True

    def update_driver_password(
            self,
            user_uid: str,
            new_password: str
    ) -> bool:
        auth.update_user(user_uid, password=new_password, app=self._app)
        return True

    def update_driver_phone_number(
            self,
            user_uid: str,
            new_phone_number: str
    ) -> bool:
        auth.update_user(user_uid, phone_number=new_phone_number, app=self._app)
        return True

    def update_admin_user(
            self,
            user_uid: str,
            email: str,
    ) -> bool:
        result: bool = False
        self._logger.info(f"Updating user with email: {email}")
        try:
            auth.update_user(uid=user_uid, email=email, app=self._app)
            result = True
        except Exception as e:
            self._logger.error(f"Failed to update user with email: {email}, error: {e}")
        return result

firebase_handler = FirebaseHandler()