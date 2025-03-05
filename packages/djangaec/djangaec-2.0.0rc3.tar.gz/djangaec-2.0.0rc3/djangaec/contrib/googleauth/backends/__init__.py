import random
import string
from django.db import (
    connections,
    router,
)
from ..models import User


def _find_atomic_decorator(model):
    connection = connections[router.db_for_read(model)]

    # FIXME: When Django GCloud Connectors gets rid of its own atomic decorator
    # the Django atomic() decorator can be used regardless

    if connection.settings_dict['ENGINE'] == 'gcloudc.db.backends.datastore':
        from gcloudc.db.transaction import atomic
    else:
        from django.db.transaction import atomic

    return atomic


def _generate_unused_username(ideal):
    """
        Check the database for a user with the specified username
        and return either that ideal username, or an unused generated
        one using the ideal username as a base
    """

    if not User.objects.filter(username_lower=ideal.lower()).exists():
        return ideal

    exists = True

    # We use random digits rather than anything sequential to avoid any kind of
    # attack vector to get this loop stuck
    while exists:
        random_digits = "".join([random.choice(string.digits) for x in range(5)])
        username = "%s-%s" % (ideal, random_digits)
        exists = User.objects.filter(username_lower=username.lower).exists()

    return username
