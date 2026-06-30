"""Shared EIP-712 encoding + signing helper.

eth_account's encode_typed_data accepts either three positional args
(domain_data, message_types, message_data) or a single full_message dict.
We use the full_message form for explicit primaryType control.
"""
from __future__ import annotations

from eth_account import Account
from eth_account.messages import encode_typed_data, SignableMessage

EIP712_DOMAIN_TYPE = [
    {"name": "name", "type": "string"},
    {"name": "version", "type": "string"},
    {"name": "chainId", "type": "uint256"},
    {"name": "verifyingContract", "type": "address"},
]


def encode_eip712(
    primary_type: str,
    types: dict,
    domain: dict,
    message: dict,
) -> SignableMessage:
    return encode_typed_data(
        full_message={
            "types": {**types, "EIP712Domain": EIP712_DOMAIN_TYPE},
            "primaryType": primary_type,
            "domain": domain,
            "message": message,
        }
    )


def sign_eip712(
    signer_key: str,
    primary_type: str,
    types: dict,
    domain: dict,
    message: dict,
) -> str:
    signable = encode_eip712(primary_type, types, domain, message)
    signed = Account.sign_message(signable, signer_key)
    sig_bytes = signed.signature
    v = sig_bytes[-1]
    if v < 27:
        sig_bytes = sig_bytes[:-1] + bytes([v + 27])
    return "0x" + sig_bytes.hex()
