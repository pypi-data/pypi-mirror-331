import json

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .aes_encryptor import AESEncryption

KEY_FOR_KEY_ENCRYPTION = getattr(settings, 'KEY_FOR_KEY_ENCRYPTION')
IV_FOR_KEY_ENCRYPTION = getattr(settings, 'IV_FOR_KEY_ENCRYPTION')
SALT_FOR_KEY_ENCRYPTION = getattr(settings, 'SALT_FOR_KEY_ENCRYPTION', '')

aes = AESEncryption()

class IpEncryptionKey(models.Model):
    """
    Stores encryption keys and IVs for each IP address.
    Only the admin should modify this table.
    """
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)
    ip_address_list = ArrayField(models.GenericIPAddressField(), blank=True, default=list)
    secrets = models.TextField()
    partner_code = models.CharField(max_length=100, unique=True)
    valid_till = models.DateTimeField(null=True)
    is_enabled = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        """
        Encrypt secrets JSON before saving.
        """

        secrets_str = json.dumps(self.secrets)
        self.secrets = aes.encrypt_aes(
            secrets_str,
            KEY_FOR_KEY_ENCRYPTION,
            IV_FOR_KEY_ENCRYPTION,
            SALT_FOR_KEY_ENCRYPTION if SALT_FOR_KEY_ENCRYPTION else None
        )

        super().save(*args, **kwargs)

    def get_secrets_data(self):
        """
        Returns decrypted secrets as a dictionary.
        """
        if self.secrets:
            decrypted_str = aes.decrypt_aes(
                self.secrets,
                KEY_FOR_KEY_ENCRYPTION,
                IV_FOR_KEY_ENCRYPTION,
                SALT_FOR_KEY_ENCRYPTION if SALT_FOR_KEY_ENCRYPTION else None
            )
            return json.loads(decrypted_str)
        return {}

    @property
    def secrets_data(self):
        return self.get_secrets_data()
