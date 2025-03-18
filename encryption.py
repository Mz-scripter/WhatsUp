from cryptography.fernet import Fernet

with open('secret.key', 'rb') as key_file:
    key = key_file.read()

fernet = Fernet(key)