import base64
import os
from typing import MutableMapping, Optional, Tuple

import streamlit as st
from cryptography import fernet
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from msal import ConfidentialClientApplication
from ace_cm import CM


def key_from_parameters(salt: bytes, iterations: int, password: str):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )

    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


# EncryptedCookieManager
class ECM(MutableMapping[str, str]):
    def __init__(
        self,
        *,
        password: str,
        path: str = None,
        prefix: str = "",
        key_params_cookie="ECM.key_params",
        ignore_broken=True,
    ):
        self._cookie_manager = CM(path=path, prefix=prefix)
        self._fernet: Optional[Fernet] = None
        self._key_params_cookie = key_params_cookie
        self._password = password
        self._ignore_broken = ignore_broken
        self.scope = ["User.Read"]
        self.redirect_uri = os.environ["REDIRECT_URI"]
        self.app = ConfidentialClientApplication(
            client_id=os.environ["CLIENT_ID"],
            client_credential=os.environ["CLIENT_SECRET"],
            authority=os.environ["AUTHORITY"],
        )

    def ready(self):
        return self._cookie_manager.ready()

    def save(self):
        return self._cookie_manager.save()

    def app_helper(self, ecm):
        auth_code = False
        if st.query_params.get("code"):
            auth_code = st.query_params["code"]
            if auth_code:
                result = self.app.acquire_token_by_authorization_code(
                    auth_code, scopes=self.scope, redirect_uri=self.redirect_uri
                )

                if "access_token" in result:
                    ecm["token"] = result["access_token"]
                    ecm["refresh_token"] = result["refresh_token"]
                    ecm["ace_username"] = result["id_token_claims"]["name"]
                    ecm["ace_useremail"] = result["id_token_claims"][
                        "preferred_username"
                    ]
                    st.write("Login successful!")
                    st.write(f"Welcome {ecm['ace_username']}")
                    ecm.save()
                    st.query_params.clear()
                    return {
                        "username": ecm["ace_username"],
                        "useremail": ecm["ace_useremail"],
                    }

                else:
                    st.warning("Login failed. Please refresh the page and try again.")
                    st.query_params.clear()
                    st.stop()
        else:
            auth_url = self.app.get_authorization_request_url(
                self.scope, redirect_uri=self.redirect_uri
            )
            st.write(f"Please go to this URL to authenticate: [Login]({auth_url})")
            st.stop()

    def _encrypt(self, value):
        self._setup_fernet()
        return self._fernet.encrypt(value)

    def _decrypt(self, value):
        self._setup_fernet()
        return self._fernet.decrypt(value)

    def _setup_fernet(self):
        if self._fernet is not None:
            return
        key_params = self._get_key_params()
        if not key_params:
            key_params = self._initialize_new_key_params()
        salt, iterations, magic = key_params
        key = key_from_parameters(
            salt=salt, iterations=iterations, password=self._password
        )

        self._fernet = Fernet(key)

    def _get_key_params(self) -> Optional[Tuple[bytes, int, bytes]]:
        raw_key_params = self._cookie_manager.get(self._key_params_cookie)
        if not raw_key_params:
            return
        try:
            raw_salt, raw_iterations, raw_magic = raw_key_params.split(":")
            return (
                base64.b64decode(raw_salt),
                int(raw_iterations),
                base64.b64decode(raw_magic),
            )
        except (ValueError, TypeError):
            print(f"Failed to parse key parameters from cookie {raw_key_params}")
            return

    def _initialize_new_key_params(self) -> Tuple[bytes, int, bytes]:
        salt = os.urandom(16)
        iterations = 390000
        magic = os.urandom(16)
        self._cookie_manager[self._key_params_cookie] = b":".join(
            [
                base64.b64encode(salt),
                str(iterations).encode("ascii"),
                base64.b64encode(magic),
            ]
        ).decode("ascii")
        return salt, iterations, magic

    def __repr__(self):
        if self.ready():
            return f"<ECM: {dict(self)!r}>"
        return "<ECM: not ready>"

    def __getitem__(self, k: str) -> str:
        try:
            return self._decrypt(self._cookie_manager[k].encode("utf-8")).decode(
                "utf-8"
            )
        except fernet.InvalidToken:
            if self._ignore_broken:
                return
            raise

    def __iter__(self):
        return iter(self._cookie_manager)

    def __len__(self):
        return len(self._cookie_manager)

    def __setitem__(self, key: str, value: str) -> None:
        self._cookie_manager[key] = self._encrypt(value.encode("utf-8")).decode("utf-8")

    def __delitem__(self, key: str) -> None:
        del self._cookie_manager[key]
