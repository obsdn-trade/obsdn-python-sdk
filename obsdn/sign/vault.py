from __future__ import annotations

from obsdn.sign._encode import sign_eip712

CREATE_VAULT_TYPES = {
    "CreateVault": [
        {"name": "main", "type": "address"},
        {"name": "vault", "type": "address"},
        {"name": "profitShareBps", "type": "uint256"},
    ],
}

STAKE_VAULT_TYPES = {
    "StakeVault": [
        {"name": "vault", "type": "address"},
        {"name": "staker", "type": "address"},
        {"name": "token", "type": "address"},
        {"name": "amount", "type": "uint256"},
        {"name": "nonce", "type": "uint64"},
    ],
}

UNSTAKE_VAULT_TYPES = {
    "UnstakeVault": [
        {"name": "vault", "type": "address"},
        {"name": "staker", "type": "address"},
        {"name": "token", "type": "address"},
        {"name": "amount", "type": "uint256"},
        {"name": "nonce", "type": "uint64"},
    ],
}


def sign_create_vault(
    signer_key: str, domain: dict, main: str, vault: str, profit_share_bps: int
) -> str:
    msg = {"main": main, "vault": vault, "profitShareBps": profit_share_bps}
    return sign_eip712(signer_key, "CreateVault", CREATE_VAULT_TYPES, domain, msg)


def sign_stake_vault(
    signer_key: str, domain: dict, vault: str, staker: str, token: str, amount: int, nonce: int
) -> str:
    msg = {"vault": vault, "staker": staker, "token": token, "amount": amount, "nonce": nonce}
    return sign_eip712(signer_key, "StakeVault", STAKE_VAULT_TYPES, domain, msg)


def sign_unstake_vault(
    signer_key: str, domain: dict, vault: str, staker: str, token: str, amount: int, nonce: int
) -> str:
    msg = {"vault": vault, "staker": staker, "token": token, "amount": amount, "nonce": nonce}
    return sign_eip712(signer_key, "UnstakeVault", UNSTAKE_VAULT_TYPES, domain, msg)
