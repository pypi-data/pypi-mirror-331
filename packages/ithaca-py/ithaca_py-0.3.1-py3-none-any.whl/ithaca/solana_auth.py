"""Solana Auth Modeule."""

import base58
import solders

from .auth import Auth
from .logger import logger


class SolanaAuth(Auth):
    """Handle authentication processes, message signing."""

    def __init__(self, parent, private_key: str):
        """
        Initialize the authentication handler.

        Args:
            parent: The parent context or object that holds the Auth instance.
            private_key (str): base58 private key.
        """
        self.parent = parent
        self.private_key = private_key
        self.keypair = solders.keypair.Keypair.from_base58_string(private_key)
        self.parent.address = str(self.keypair.pubkey())
        self.parent.account = self.keypair

    def request_auth(self):
        """Request a nonce for authentication from the server."""
        credentials = {"ethAddress": str(self.keypair.pubkey())}
        return self.parent.post("/auth/requestAuth", json=credentials)

    def sign_message(self, message: str):
        """Sign the nonce with the private key."""

        signature = self.keypair.sign_message(bytes(message.encode()))
        signature_base58 = base58.b58encode(signature.to_bytes()).decode("utf-8")
        return signature_base58

    def login(self) -> bool:
        """
        Attempt to log in using Ethereum signature-based authentication.

        Returns:
            True if login was successful, False otherwise.
        """
        logger.debug("Attempting login...")
        nonce_response = self.request_auth()
        nonce = nonce_response.get("nonce")
        if nonce:
            logger.debug("Received nonce")
            signature = self.sign_message(nonce)
            auth_response = self.parent.post(
                "/auth/validateAuth", json={"nonce": nonce, "signature": signature}
            )
            if "payload" in auth_response:
                self.parent.user = auth_response["payload"]
                logger.debug("Login successful.")
                return True
            else:
                logger.debug("Login failed. No payload in auth response.")
        else:
            logger.debug("Login failed. No nonce received.")

        return False
