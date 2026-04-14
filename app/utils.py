from cryptography.fernet import Fernet
from django.conf import settings
import base64

def get_cipher():
    # Django SECRET_KEY ni 32 baytli kalitga aylantiramiz
    key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
    return Fernet(key)

def encrypt_password(password):
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    cipher = get_cipher()
    return cipher.decrypt(encrypted_password.encode()).decode()