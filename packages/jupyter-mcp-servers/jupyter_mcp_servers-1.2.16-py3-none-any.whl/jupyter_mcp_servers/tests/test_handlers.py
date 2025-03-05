# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import json

from .._version import __version__


async def test_config(jp_fetch):
    # When
    response = await jp_fetch("jupyter_mcp_servers", "config")
    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "extension": "jupyter_mcp_servers",
        "version": __version__
    }
