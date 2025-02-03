from cryptography.fernet import Fernet

def generate_encryption_key():
    key = Fernet.generate_key()
    print(f"Generated Encryption Key: {key.decode()}")
    print("\nAdd this to your .env file as:")
    print(f"ENCRYPTION_KEY={key.decode()}")

if __name__ == "__main__":
    generate_encryption_key() 