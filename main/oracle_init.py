from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def patch_oracle_session(sender, connection, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")
        cursor.execute("ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
        cursor.execute("ALTER SESSION SET NLS_TIMESTAMP_TZ_FORMAT = 'YYYY-MM-DD HH24:MI:SS TZR'")