"""Enterprise headers utilities."""

import json
from typing import Dict, Union

from src.core.config import settings


def add_ent_headers(
    default_headers: Dict[str, str], ent_headers: Union[Dict[str, str], str]
) -> Dict[str, str]:
    """
    Updates the default headers with enterprise-specific headers.

    Args:
        default_headers: A dictionary containing the default headers.
        ent_headers: A dictionary or JSON string containing enterprise-specific headers.

    Returns:
        The updated dictionary of headers including enterprise-specific headers.

    Raises:
        json.JSONDecodeError: If ent_headers is a string and cannot be parsed as JSON.
    """
    # Parse ent_headers if it's a string
    parsed_headers = _parse_enterprise_headers(ent_headers)

    for key in settings.enterprise_llm_headers:
        if key in parsed_headers:
            default_headers[key] = parsed_headers[key]

    return default_headers


def _parse_enterprise_headers(
    ent_headers: Union[Dict[str, str], str],
) -> Dict[str, str]:
    """
    Parse enterprise headers from string or return as-is if already a dictionary.

    Args:
        ent_headers: Enterprise headers as dictionary or JSON string.

    Returns:
        Parsed enterprise headers as dictionary.

    Raises:
        json.JSONDecodeError: If ent_headers is a string and cannot be parsed as JSON.
    """
    if isinstance(ent_headers, str):
        return json.loads(ent_headers)

    return ent_headers
