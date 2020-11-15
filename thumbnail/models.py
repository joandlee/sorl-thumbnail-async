from copy import copy
from django.db.models import signals
from django.dispatch import receiver

from .conf import settings
from .tasks import create_thumbnail

class AsyncThumbnailMixin(object):
    """
    All model which have ImageField to be thumbnailed inheret from this class.
    """
    image_field_name = [{'field': 'picture', 'is_cover': False}]

    def call_upload_task(self):
        for name, options in settings.OPTIONS_DICT.items():
            opt = copy(options)
            geometry = opt.pop('geometry')
            for img in self.image_field_name:
                if (name == 'cover' and img["is_cover"]) or (name != 'cover'):
                    create_thumbnail.delay(getattr(self, img["field"]), geometry, **opt)

    def save(self, *args, **kwargs):
        super(AsyncThumbnailMixin, self).save(*args, **kwargs)
        self.call_upload_task()
