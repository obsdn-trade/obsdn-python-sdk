"""Golden hash tests: Python EIP-712 signing must produce byte-equal
struct hashes, digests, and signatures against the exchange's reference signer.

Fixtures under tests/fixtures/eip712/*.json are copied from the Rust SDK.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from eth_account import Account as EthAccount
from eth_account.messages import encode_typed_data
from eth_utils import keccak

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "eip712"

# Template -> (primaryType, types dict, message builder)
# Each builder takes fixture["input"] and returns the EIP-712 message dict.

TEMPLATES: dict[str, tuple[str, dict, callable]] = {
    "Order": (
        "Order",
        {
            "Order": [
                {"name": "sender", "type": "address"},
                {"name": "marketIndex", "type": "uint16"},
                {"name": "side", "type": "uint8"},
                {"name": "size", "type": "uint128"},
                {"name": "price", "type": "uint128"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "sender": inp["sender"],
            "marketIndex": inp["market_index"],
            "side": 0 if inp["side"] == "buy" else 1,
            "size": int(inp["size"]),
            "price": int(inp["price"]),
            "nonce": int(inp["nonce"]),
        },
    ),
    "Transfer": (
        "Transfer",
        {
            "Transfer": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "token", "type": "address"},
                {"name": "amount", "type": "uint128"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "from": inp["from"],
            "to": inp["to"],
            "token": inp["token"],
            "amount": int(inp["amount"]),
            "nonce": int(inp["nonce"]),
        },
    ),
    "Withdraw": (
        "Withdraw",
        {
            "Withdraw": [
                {"name": "sender", "type": "address"},
                {"name": "token", "type": "address"},
                {"name": "amount", "type": "uint128"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "sender": inp["sender"],
            "token": inp["token"],
            "amount": int(inp["amount"]),
            "nonce": int(inp["nonce"]),
        },
    ),
    "CreateVault": (
        "CreateVault",
        {
            "CreateVault": [
                {"name": "main", "type": "address"},
                {"name": "vault", "type": "address"},
                {"name": "profitShareBps", "type": "uint256"},
            ],
        },
        lambda inp: {
            "main": inp["main"],
            "vault": inp["vault"],
            "profitShareBps": int(inp["profit_share_bps"]),
        },
    ),
    "StakeVault": (
        "StakeVault",
        {
            "StakeVault": [
                {"name": "vault", "type": "address"},
                {"name": "staker", "type": "address"},
                {"name": "token", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "vault": inp["vault"],
            "staker": inp["staker"],
            "token": inp["token"],
            "amount": int(inp["amount"]),
            "nonce": int(inp["nonce"]),
        },
    ),
    "UnstakeVault": (
        "UnstakeVault",
        {
            "UnstakeVault": [
                {"name": "vault", "type": "address"},
                {"name": "staker", "type": "address"},
                {"name": "token", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "vault": inp["vault"],
            "staker": inp["staker"],
            "token": inp["token"],
            "amount": int(inp["amount"]),
            "nonce": int(inp["nonce"]),
        },
    ),
    "CreateSubaccount": (
        "CreateSubaccount",
        {
            "CreateSubaccount": [
                {"name": "main", "type": "address"},
                {"name": "subaccount", "type": "address"},
            ],
        },
        lambda inp: {
            "main": inp["main"],
            "subaccount": inp["subaccount"],
        },
    ),
    "Register": (
        "Register",
        {
            "Register": [
                {"name": "sender", "type": "address"},
                {"name": "signer", "type": "address"},
                {"name": "message", "type": "string"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "sender": inp["sender"],
            "signer": inp["signer"],
            "message": inp["message"],
            "nonce": int(inp["nonce"]),
        },
    ),
    "DelegatedSigner": (
        "DelegatedSigner",
        {
            "DelegatedSigner": [
                {"name": "account", "type": "address"},
            ],
        },
        lambda inp: {
            "account": inp["account"],
        },
    ),
    "RegisterChildAccountSigner": (
        "RegisterChildAccountSigner",
        {
            "RegisterChildAccountSigner": [
                {"name": "main", "type": "address"},
                {"name": "childAccount", "type": "address"},
                {"name": "signer", "type": "address"},
                {"name": "message", "type": "string"},
                {"name": "nonce", "type": "uint64"},
            ],
        },
        lambda inp: {
            "main": inp["main"],
            "childAccount": inp["child_account"],
            "signer": inp["signer"],
            "message": inp["message"],
            "nonce": int(inp["nonce"]),
        },
    ),
}

FIXTURE_TO_TEMPLATE = {
    "order": "Order",
    "transfer": "Transfer",
    "withdraw": "Withdraw",
    "create_vault": "CreateVault",
    "stake_vault": "StakeVault",
    "unstake_vault": "UnstakeVault",
    "create_subaccount": "CreateSubaccount",
    "register_signed_by_sender": "Register",
    "register_signed_by_signer": "DelegatedSigner",
    "register_child_account_signer": "RegisterChildAccountSigner",
}


def _load_fixture(name: str) -> dict:
    path = FIXTURES_DIR / f"{name}.json"
    with open(path) as f:
        return json.load(f)


def _fixture_domain(d: dict) -> dict:
    return {
        "name": d["name"],
        "version": d["version"],
        "chainId": int(d["chain_id"]),
        "verifyingContract": d["verifying_contract"],
    }


def _eip712_domain_type() -> list:
    return [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ]


def _parse_sig(hex_sig: str) -> bytes:
    return bytes.fromhex(hex_sig.removeprefix("0x"))


@pytest.mark.parametrize("fixture_name", list(FIXTURE_TO_TEMPLATE.keys()))
def test_golden_signature(fixture_name: str):
    f = _load_fixture(fixture_name)
    template_name = FIXTURE_TO_TEMPLATE[fixture_name]
    primary_type, types, msg_builder = TEMPLATES[template_name]
    domain = _fixture_domain(f["domain"])
    msg = msg_builder(f["input"])

    signable = encode_typed_data(
        full_message={
            "types": {**types, "EIP712Domain": _eip712_domain_type()},
            "primaryType": primary_type,
            "domain": domain,
            "message": msg,
        }
    )

    # header = domain separator, body = struct hash
    domain_sep = signable.header
    struct_hash = signable.body

    # Assert domain separator
    expected_domain_sep = bytes.fromhex(f["domain_separator"].removeprefix("0x"))
    assert domain_sep == expected_domain_sep, (
        f"{fixture_name}: domain_separator mismatch\n"
        f"  got:      0x{domain_sep.hex()}\n"
        f"  expected: {f['domain_separator']}"
    )

    # Assert struct hash
    expected_struct_hash = bytes.fromhex(f["struct_hash"].removeprefix("0x"))
    assert struct_hash == expected_struct_hash, (
        f"{fixture_name}: struct_hash mismatch\n"
        f"  got:      0x{struct_hash.hex()}\n"
        f"  expected: {f['struct_hash']}"
    )

    # Assert digest (signing hash = keccak(0x1901 || domainSep || structHash))
    digest = keccak(b"\x19\x01" + domain_sep + struct_hash)
    expected_digest = bytes.fromhex(f["digest"].removeprefix("0x"))
    assert digest == expected_digest, (
        f"{fixture_name}: digest mismatch\n  got:      0x{digest.hex()}\n  expected: {f['digest']}"
    )

    # Sign and verify signature matches
    signed = EthAccount.sign_message(signable, f["private_key"])
    sig_bytes = signed.signature
    v = sig_bytes[-1]
    if v < 27:
        sig_bytes = sig_bytes[:-1] + bytes([v + 27])

    expected_sig = _parse_sig(f["signature"])
    assert sig_bytes == expected_sig, (
        f"{fixture_name}: signature mismatch\n"
        f"  got:      0x{sig_bytes.hex()}\n"
        f"  expected: {f['signature']}"
    )

    # Verify signer address
    acct = EthAccount.from_key(f["private_key"])
    assert acct.address.lower() == f["signer_address"].lower(), (
        f"{fixture_name}: signer address mismatch"
    )
