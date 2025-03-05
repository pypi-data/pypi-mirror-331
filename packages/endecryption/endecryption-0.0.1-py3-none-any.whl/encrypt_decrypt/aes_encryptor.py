import base64
import hashlib

import simplejson as json
from Crypto.Cipher import AES
from typing import Union


class AESEncryption:
    def __init__(self):
        self.AES_BLOCK_SIZE = 32

    def pad(self, input_string: str) -> bytes:
        """Pad the input string to the block size.
         For Adding the padding character the chr(the number required to
         make input_string a perfect multiple of block_size) is used."""

        pad_len = self.AES_BLOCK_SIZE - (len(input_string) % self.AES_BLOCK_SIZE)
        return bytes(input_string + pad_len * chr(pad_len), 'utf-8')


    def unpad(self, input_string: str) -> str:
        """Remove the padding from the input string.
         The padding character is the last character of the input string.
         And the number of padding characters is ASCII value of the last
         character."""

        return input_string[:-ord(input_string[-1])]


    def generate_hash(self, input_string: Union[str, list, dict]) -> str:
        """
        Generate a hash of the almost any json serializable types.

        Note -> For generating hash of complex type like
                QuerySet or Model, a specific serializer class is required
                (applying rest_framework.parsers.JSONParser is also required)
        """
        if isinstance(input_string, str):
            input_string = input_string.encode("utf-8")
        elif isinstance(input_string, (list, dict)):
            input_string = json.dumps(input_string).encode("utf-8")
        else:
            raise Exception("invalid input format")
        return hashlib.sha256(input_string).hexdigest()


    def encrypt_aes(self, plain_text: str, key: str, initialization_vector: str,
                    salt: str = None) -> str:
        """ CBC -> Cipher Block Chaining
        AES has 3 modes of operation:
            The first block is XORed with the IV (initialization vector).
            The second block is XORed with the first encrypted block.
            The third block is XORed with the second encrypted block.
        Algo->
            1. The first block is XORed with the IV (initialization vector).
            2. Then the first block is encrypted with Key.
            3. The second block is XORed with the first encrypted block.
            4. Then the second block is encrypted with Key.
            5. The third block is XORed with the second encrypted block.
            6. Then the third block is encrypted with Key.
        """
        if salt:
            plain_text += salt

        plain_text = self.pad(plain_text)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC,
                         initialization_vector.encode('utf-8'))
        cipher_text: bytes = cipher.encrypt(plain_text)
        return base64.b64encode(cipher_text).decode("utf-8")


    def decrypt_aes(self, cipher_text: str, key: str, initialization_vector: str,
                    salt: str = None) -> str:
        """Decrypt the input string using the key."""
        cipher_text = base64.b64decode(cipher_text)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC,
                         initialization_vector.encode('utf-8'))
        plain_text = cipher.decrypt(cipher_text).decode("utf-8")
        plain_text = self.unpad(plain_text)

        if salt and plain_text.endswith(salt):
            plain_text = plain_text[:-len(salt)]

        return plain_text


    def validate_checksum(self, checksum: str, plain_text: str) -> bool:
        """Verify the checksum of the input string."""
        return checksum == self.generate_hash(plain_text)


    def get_aes_cbc_encrypted_data(self, plain_text: Union[dict, list], key: str,
                                   initialization_vector: str, salt: str = None
                                   ) -> dict[str, str]:
        try:
            if isinstance(plain_text, (dict, list)):
                plain_text = json.dumps(plain_text)
            checksum = self.generate_hash(plain_text)
            encrypted_payload = self.encrypt_aes(plain_text, key,
                                            initialization_vector, salt)
            return {
                "checksum": checksum,
                "payload": encrypted_payload
            }
        except:
            raise Exception("Encryption Failed")


    def get_aes_cbc_decrypted_data(self, checksum: str, encrypted_payload: str,
                                   key: str, initialization_vector: str,
                                   salt: str = None) -> str:
        """Verify the checksum of the input string."""
        try:
            decrypted_payload = self.decrypt_aes(encrypted_payload, key,
                                            initialization_vector, salt)
        except:
            raise Exception("Decryption Failed")

        if not self.validate_checksum(checksum, decrypted_payload):
            raise Exception("Checksum Verification Failed")
        return decrypted_payload


    def get_ip_address(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
