from __future__ import annotations

from obsdn.sign._encode import encode_eip712, sign_eip712

ORDER_TYPES = {
    "Order": [
        {"name": "sender", "type": "address"},
        {"name": "marketIndex", "type": "uint16"},
        {"name": "side", "type": "uint8"},
        {"name": "size", "type": "uint128"},
        {"name": "price", "type": "uint128"},
        {"name": "nonce", "type": "uint64"},
    ],
}


def sign_order(
    signer_key: str,
    domain: dict,
    sender: str,
    market_index: int,
    side: int,
    size: int,
    price: int,
    nonce: int,
) -> str:
    msg = _build_message(sender, market_index, side, size, price, nonce)
    return sign_eip712(signer_key, "Order", ORDER_TYPES, domain, msg)


def order_signing_hash(
    domain: dict,
    sender: str,
    market_index: int,
    side: int,
    size: int,
    price: int,
    nonce: int,
) -> bytes:
    msg = _build_message(sender, market_index, side, size, price, nonce)
    return encode_eip712("Order", ORDER_TYPES, domain, msg).body


def _build_message(
    sender: str, market_index: int, side: int, size: int, price: int, nonce: int
) -> dict:
    return {
        "sender": sender,
        "marketIndex": market_index,
        "side": side,
        "size": size,
        "price": price,
        "nonce": nonce,
    }
