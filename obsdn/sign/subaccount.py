from __future__ import annotations

from obsdn.sign._encode import sign_eip712

CREATE_SUBACCOUNT_TYPES = {
    "CreateSubaccount": [
        {"name": "main", "type": "address"},
        {"name": "subaccount", "type": "address"},
    ],
}

REGISTER_CHILD_ACCOUNT_SIGNER_TYPES = {
    "RegisterChildAccountSigner": [
        {"name": "main", "type": "address"},
        {"name": "childAccount", "type": "address"},
        {"name": "signer", "type": "address"},
        {"name": "message", "type": "string"},
        {"name": "nonce", "type": "uint64"},
    ],
}


def sign_create_subaccount(signer_key: str, domain: dict, main: str, subaccount: str) -> str:
    msg = {"main": main, "subaccount": subaccount}
    return sign_eip712(signer_key, "CreateSubaccount", CREATE_SUBACCOUNT_TYPES, domain, msg)


def sign_register_child_account_signer(
    signer_key: str,
    domain: dict,
    main: str,
    child_account: str,
    signer: str,
    message: str,
    nonce: int,
) -> str:
    msg = {
        "main": main,
        "childAccount": child_account,
        "signer": signer,
        "message": message,
        "nonce": nonce,
    }
    return sign_eip712(
        signer_key,
        "RegisterChildAccountSigner",
        REGISTER_CHILD_ACCOUNT_SIGNER_TYPES,
        domain,
        msg,
    )
