from __future__ import annotations

import os

import pytest

from obsdn.client import Client
from obsdn.env import Env

STAGING_API_KEY = os.environ.get("OBSDN_TEST_API_KEY", "")
STAGING_API_SECRET = os.environ.get("OBSDN_TEST_API_SECRET", "")
STAGING_SIGNER_KEY = os.environ.get("OBSDN_TEST_SIGNER_KEY", "")

has_credentials = bool(STAGING_API_KEY and STAGING_API_SECRET)
has_signer_key = bool(STAGING_SIGNER_KEY)

skip_no_creds = pytest.mark.skipif(
    not has_credentials, reason="OBSDN_TEST_API_KEY/SECRET not set"
)
skip_no_key = pytest.mark.skipif(
    not has_signer_key, reason="OBSDN_TEST_SIGNER_KEY not set"
)


@pytest.fixture
async def public_client():
    async with Client(env=Env.STAGING) as c:
        yield c


@pytest.fixture
async def auth_client():
    async with Client(
        env=Env.STAGING,
        api_key=STAGING_API_KEY,
        api_secret=STAGING_API_SECRET,
        signer_key=STAGING_SIGNER_KEY or None,
    ) as c:
        yield c
