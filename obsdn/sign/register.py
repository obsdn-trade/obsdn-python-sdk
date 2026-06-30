from __future__ import annotations

from obsdn.sign._encode import sign_eip712

REGISTER_TYPES = {
    "Register": [
        {"name": "sender", "type": "address"},
        {"name": "signer", "type": "address"},
        {"name": "message", "type": "string"},
        {"name": "nonce", "type": "uint64"},
    ],
}

DELEGATED_SIGNER_TYPES = {
    "DelegatedSigner": [
        {"name": "account", "type": "address"},
    ],
}


def sign_register(
    signer_key: str,
    domain: dict,
    sender: str,
    signer: str,
    message: str,
    nonce: int,
) -> str:
    msg = {"sender": sender, "signer": signer, "message": message, "nonce": nonce}
    return sign_eip712(signer_key, "Register", REGISTER_TYPES, domain, msg)


def sign_delegated_signer(
    signer_key: str,
    domain: dict,
    account: str,
) -> str:
    msg = {"account": account}
    return sign_eip712(signer_key, "DelegatedSigner", DELEGATED_SIGNER_TYPES, domain, msg)
