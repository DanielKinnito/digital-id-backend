from cryptography.fernet import Fernet
import secrets

def generate_encryption_key():
    key = Fernet.generate_key()
    print(f"Generated Encryption Key: {key.decode()}")
    print("\nAdd this to your .env file as:")
    print(f"ENCRYPTION_KEY={key.decode()}")

def generate_jwt_secret_key():
    # Generate a cryptographically secure JWT secret key.
    # Adjust the byte size if needed (32 bytes here for a strong secret).
    key = secrets.token_urlsafe(32)
    print(f"Generated JWT Secret Key: {key}")
    print("\nAdd this to your .env file as:")
    print(f"JWT_SECRET_KEY={key}")

if __name__ == "__main__":
    generate_encryption_key()
    print("\n" + "="*60 + "\n")
    generate_jwt_secret_key()
