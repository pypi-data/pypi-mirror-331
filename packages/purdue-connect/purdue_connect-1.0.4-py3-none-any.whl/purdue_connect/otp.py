import base64
import requests
from urllib.parse import urlparse, parse_qs
from Crypto.PublicKey import RSA
import pyotp
import qrcode
import qrcode.image.svg
from .config import load_config, save_config
from . import hotp_activation

def set_hotp_secret(secret):
    """
    Save the provided HOTP secret into persistent configuration.
    """
    config = load_config()
    # Store the secret as a string.
    config["hotp_secret"] = secret.decode() if isinstance(secret, bytes) else secret
    # Initialize counter if not already set.
    config.setdefault("counter", 1)
    save_config(config)
    print("HOTP secret has been set successfully.")

def hotp(secret, counter, digits=6):
    """
    Generate the OTP using pyotp.
    """
    # pyotp expects the secret to be Base32-encoded.
    hotp_instance = pyotp.HOTP(secret)
    otp = hotp_instance.at(counter)
    return otp

def get_next_otp():
    """
    Returns the next OTP and increments the counter.
    """
    config = load_config()
    secret = config.get("hotp_secret")
    if not secret:
        raise ValueError("HOTP secret not set. Please set it using an activation URI (link or QR).")
    counter = config.get("counter", 1)
    otp = hotp(secret, counter)
    config["counter"] = counter + 1
    save_config(config)
    return otp

# Backward compatibility helper functions:
def set_hotp_secret_from_link(link):
    set_hotp_secret_from_activation_uri(link)

def set_hotp_secret_from_qr(qr_uri):
    set_hotp_secret_from_activation_uri(qr_uri)

def set_hotp_secret_from_activation_uri(uri):
    try:
        secret = hotp_activation.get_secret(uri)
        set_hotp_secret(secret)
    except Exception as e:
        print(f"Error extracting secret from activation URI: {e}")
