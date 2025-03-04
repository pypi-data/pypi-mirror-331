# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "LamIntegrationRunParamsBase",
    "Advanced",
    "AdvancedProxy",
    "LamIntegrationRunParamsNonStreaming",
    "LamIntegrationRunParamsStreaming",
]


class LamIntegrationRunParamsBase(TypedDict, total=False):
    raccoon_passcode: Required[str]
    """
    The raccoon passcode associated with the end user on behalf of which the call is
    being made.
    """

    advanced: Optional[Advanced]
    """
    Advanced configuration options for the session, such as ad-blocking and CAPTCHA
    solving.
    """

    integration_id: Optional[str]
    """The unique identifier for the integration being called."""

    properties: Optional[object]
    """Additional properties or data related to the particular integration."""


class AdvancedProxy(TypedDict, total=False):
    city: Optional[str]
    """Target city."""

    country: Optional[str]
    """Target country (2-letter ISO code)."""

    enable: bool
    """Whether to use a proxy for the browser session."""

    state: Optional[str]
    """Target state (2-letter code)."""

    zip: Optional[int]
    """Target postal code."""


class Advanced(TypedDict, total=False):
    block_ads: Optional[bool]
    """Whether to block advertisements during the browser session."""

    extension_ids: Optional[Iterable[object]]
    """list of extension ids"""

    proxy: Optional[AdvancedProxy]
    """Proxy details for the browser session."""

    solve_captchas: Optional[bool]
    """Whether to attempt automatic CAPTCHA solving."""


class LamIntegrationRunParamsNonStreaming(LamIntegrationRunParamsBase, total=False):
    stream: Optional[Literal[False]]
    """Whether the response should be streamed back or not."""


class LamIntegrationRunParamsStreaming(LamIntegrationRunParamsBase):
    stream: Required[Literal[True]]
    """Whether the response should be streamed back or not."""


LamIntegrationRunParams = Union[LamIntegrationRunParamsNonStreaming, LamIntegrationRunParamsStreaming]
