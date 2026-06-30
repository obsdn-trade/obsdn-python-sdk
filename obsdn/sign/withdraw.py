from __future__ import annotations

from obsdn.sign._encode import sign_eip712

WITHDRAW_TYPES = {
    "Withdraw": [
        {"name": "sender", "type": "address"},
        {"name": "token", "type": "address"},
        {"name": "amount", "type": "uint128"},
        {"name": "nonce", "type": "uint64"},
    ],
}


def sign_withdraw(
    signer_key: str,
    domain: dict,
    sender: str,
    token: str,
    amount: int,
    nonce: int,
) -> str:
    msg = {"sender": sender, "token": token, "amount": amount, "nonce": nonce}
    return sign_eip712(signer_key, "Withdraw", WITHDRAW_TYPES, domain, msg)
