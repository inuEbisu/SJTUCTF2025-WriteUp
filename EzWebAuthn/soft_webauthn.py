"""
Module implementing software webauthn token for testing webauthn enabled
applications
"""

import json
import os
from base64 import urlsafe_b64encode
from struct import pack
from typing import Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from fido2 import cbor
from fido2.cose import ES256
from fido2.webauthn import AttestedCredentialData
from fido2.utils import sha256


def b64(msg: Union[bytes, str]) -> str:
    if isinstance(msg, str):
        msg = msg.encode("utf-8")
    return urlsafe_b64encode(msg).decode("utf-8").rstrip("=")


class SoftWebauthnDevice:
    """
    This simulates the Webauthn browser API with a authenticator device
    connected. It's primary use-case is testing, device can hold only
    one credential.
    """

    def __init__(self):
        self.credential_id = None
        self.private_key = None
        self.aaguid = b"\x00" * 16
        self.rp_id = None
        self.user_handle = None
        self.sign_count = 0

    def cred_init(
        self, rp_id, user_handle, credential_id=b"0123456789ABCDEF0123456789ABCDEF"
    ):
        """initialize credential for rp_id under user_handle"""

        # self.credential_id = os.urandom(32)
        self.credential_id = credential_id
        self.private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        self.rp_id = rp_id
        self.user_handle = user_handle

    def cred_as_attested(self):
        """return current credential as AttestedCredentialData"""

        return AttestedCredentialData.create(
            self.aaguid,
            self.credential_id,
            ES256.from_cryptography_key(self.private_key.public_key()),
        )

    def create(self, options, origin, credential_id=b"ABC"):
        """create credential and return PublicKeyCredential object aka attestation"""

        if {"alg": -7, "type": "public-key"} not in options["publicKey"][
            "pubKeyCredParams"
        ]:
            raise ValueError(
                "Requested pubKeyCredParams does not contain supported type"
            )

        if ("attestation" in options["publicKey"]) and (
            options["publicKey"]["attestation"] not in [None, "none"]
        ):
            raise ValueError("Only none attestation supported")

        # prepare new key
        self.cred_init(
            options["publicKey"]["rp"]["id"],
            options["publicKey"]["user"]["id"],
            credential_id,
        )

        # generate credential response
        client_data = {
            "type": "webauthn.create",
            # 'challenge': urlsafe_b64encode(options['publicKey']['challenge']).decode('ascii').rstrip('='),
            "challenge": options["publicKey"]["challenge"],
            "origin": origin,
        }

        rp_id_hash = sha256(self.rp_id.encode("utf-8"))
        flags = b"\x41"  # attested_data + user_present
        sign_count = pack(">I", self.sign_count)
        credential_id_length = pack(">H", len(self.credential_id))
        cose_key = cbor.encode(
            ES256.from_cryptography_key(self.private_key.public_key())
        )
        attestation_object = {
            "authData": rp_id_hash
            + flags
            + sign_count
            + self.aaguid
            + credential_id_length
            + self.credential_id
            + cose_key,
            "fmt": "none",
            "attStmt": {},
        }

        return {
            "id": b64(self.credential_id),
            "rawId": b64(self.credential_id),
            "response": {
                "clientDataJSON": b64(
                    json.dumps(client_data).replace(" ", "").encode("utf-8")
                ),
                "attestationObject": b64(cbor.encode(attestation_object)),
            },
            "type": "public-key",
        }

    def get(self, options, origin):
        """get authentication credential aka assertion"""

        if self.rp_id != options["publicKey"]["rpId"]:
            raise ValueError("Requested rpID does not match current credential")

        self.sign_count += 1

        # prepare signature
        client_data = (
            json.dumps(
                {
                    "type": "webauthn.get",
                    "challenge": options["publicKey"]["challenge"],
                    "origin": origin,
                }
            )
            .replace(" ", "")
            .encode("utf-8")
        )
        client_data_hash = sha256(client_data)

        rp_id_hash = sha256(self.rp_id.encode("utf-8"))
        flags = b"\x01"
        sign_count = pack(">I", self.sign_count)
        authenticator_data = rp_id_hash + flags + sign_count

        signature = self.private_key.sign(
            authenticator_data + client_data_hash, ec.ECDSA(hashes.SHA256())
        )

        # generate assertion
        return {
            "id": b64(self.credential_id),
            "rawId": b64(self.credential_id),
            "response": {
                "authenticatorData": b64(authenticator_data),
                "clientDataJSON": b64(client_data),
                "signature": b64(signature),
                "userHandle": b64(self.user_handle),
            },
            "type": "public-key",
        }
