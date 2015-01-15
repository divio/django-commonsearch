# -*- coding: utf-8 -*-
from django.conf import settings

from haystack.constants import DEFAULT_ALIAS


def language_from_alias(alias):
    """
    Returns alias if alias is a valid language.
    """
    if alias == DEFAULT_ALIAS:
        language = settings.LANGUAGE_CODE
    else:
        languages = [language[0] for language in settings.LANGUAGES]
        language = alias if alias in languages else None
    return language
