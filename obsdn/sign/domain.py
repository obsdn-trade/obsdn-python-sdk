from __future__ import annotations

from obsdn.env import CustomEnv, Env
from obsdn.error import ConfigError

STAGING_DOMAIN = {
    "name": "Obsidian",
    "version": "1",
    "chainId": 10143,
    "verifyingContract": "0xB95aE40b700FDBb0906b8Dc2AeBBDd94848325Df",
}

PRODUCTION_DOMAIN = {
    "name": "Obsidian",
    "version": "1",
    "chainId": 143,
    "verifyingContract": "0x90c3747cd4E6bC6FbebB1b3C54D99737590eBE45",
}


def get_domain(env: Env | CustomEnv) -> dict:
    if isinstance(env, CustomEnv):
        raise ConfigError(
            "CustomEnv requires an explicit domain dict - "
            "the SDK cannot guess chain_id / verifyingContract"
        )
    if env == Env.STAGING:
        return STAGING_DOMAIN
    return PRODUCTION_DOMAIN
