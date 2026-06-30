from __future__ import annotations

from obsdn.sign._encode import sign_eip712

TRANSFER_TYPES = {
    "Transfer": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "token", "type": "address"},
        {"name": "amount", "type": "uint128"},
        {"name": "nonce", "type": "uint64"},
    ],
}


def sign_transfer(
    private_key: str,
    domain: dict,
    from_addr: str,
    to_addr: str,
    token: str,
    amount: int,
    nonce: int,
) -> str:
    msg = {"from": from_addr, "to": to_addr, "token": token, "amount": amount, "nonce": nonce}
    return sign_eip712(private_key, "Transfer", TRANSFER_TYPES, domain, msg)
