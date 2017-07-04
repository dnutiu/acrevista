from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from django.core.exceptions import ValidationError
import magic


# This validator is used by the submit_paper view to validate the length of the author fields.
# In case the user removes a field via inspect element.
def validate_authors(*args):
    if len(args) > 0:
        # Validate the length of each row to be the same.
        len_check = len(args[0])
        for el in args:
            if len(el) != len_check and len(el) < 255:  # 255 is the max value from Author model.
                return False
        return True
    return False


@deconstructible
class FileValidator(object):
    error_messages = {
        'max_size': "Ensure this file size is not greater than %(max_size)s. Your file size is %(size)s.",
        'min_size': "Ensure this file size is not less than %(min_size)s. Your file size is %(size)s.",
        'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size),
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'], 'max_size', params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.mix_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'], 'min_size', params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            params = {'content_type': content_type}

            if content_type not in self.content_types:
                raise ValidationError(self.error_messages['content_type'], 'content_type', params)

    def __eq__(self, other):
        return isinstance(other, FileValidator)
