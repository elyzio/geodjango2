from hashids import Hashids
from django.conf import settings

hashids = Hashids(
    salt=settings.HASHIDS_SALT,
    min_length=getattr(settings, "HASHIDS_MIN_LENGTH", 8)
)

def encode_id(id):
    return hashids.encode(id)

def decode_id(hashid):
    decoded = hashids.decode(hashid)
    return decoded[0] if decoded else None
