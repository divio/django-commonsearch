# -*- coding: utf-8 -*-
from django.conf import settings

from haystack.signals import RealtimeSignalProcessor as BaseSignalProcessor


class RealtimeSignalProcessor(BaseSignalProcessor):

    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.
        """
        if 'hvad' in settings.INSTALLED_APPS:
            from hvad.models import TranslatableModel

            # Ignore translatable models
            if isinstance(instance, TranslatableModel):
                return
        super(RealtimeSignalProcessor, self).handle_save(sender, instance, **kwargs)
