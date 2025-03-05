# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["Voicev1CreateParams"]


class Voicev1CreateParams(TypedDict, total=False):
    allowed_transfer_numbers: Required[Annotated[str, PropertyInfo(alias="allowedTransferNumbers")]]

    config: Required[str]

    end_sentence: Required[Annotated[str, PropertyInfo(alias="endSentence")]]

    flow_id: Required[Annotated[str, PropertyInfo(alias="flowId")]]

    functions: Required[str]

    language: Required[str]

    model: Required[str]

    name: Required[str]

    objective: Required[str]

    phone_number: Required[Annotated[str, PropertyInfo(alias="phoneNumber")]]

    resource_keys: Required[Annotated[str, PropertyInfo(alias="resourceKeys")]]

    start_sentence: Required[Annotated[str, PropertyInfo(alias="startSentence")]]

    voice_id: Required[Annotated[str, PropertyInfo(alias="voiceId")]]

    ws_base_url: Required[Annotated[str, PropertyInfo(alias="wsBaseUrl")]]
