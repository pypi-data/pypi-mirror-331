import base64
from urllib.parse import urlparse, unquote
import requests
from Crypto.PublicKey import RSA

def qr_url_to_activation_url(qr_url):
    """
    Create activation URL from a QR URL.
    Extracts the activation code and hostname (in Base64) and returns a formatted URL.
    """
    # Extract the URL parameter value after ?value=
    data = unquote(qr_url.split("?value=")[1])
    # The first part is the activation code (remove the 'duo://' prefix)
    code = data.split("-")[0].replace("duo://", "")
    # The second part is the hostname in base64
    hostb64 = data.split("-")[1]
    # Decode the hostname (add padding if needed)
    host = base64.b64decode(hostb64 + "=" * (-len(hostb64) % 4))
    activation_url = "https://{host}/push/v2/activation/{code}".format(
        host=host.decode("utf-8"), code=code
    )
    print(activation_url)
    return activation_url

def get_secret(activation_uri):
    """
    Extracts the HOTP secret from an activation URI.
    If the URI is a QR activation URL (contains "frame/qr"), converts it first.
    Returns the HOTP secret as a Base32-encoded string.
    """
    if "frame/qr" in activation_uri:
        activation_uri = qr_url_to_activation_url(activation_uri)
    parsed = urlparse(activation_uri)
    subdomain = parsed.netloc.split(".")[0]
    host_id = subdomain.split("-")[-1]
    # Remove any trailing slash so that slug is correctly extracted.
    slug = parsed.path.rstrip("/").split("/")[-1]

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": f"api-{host_id}.duosecurity.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.0.0",
    }
    params = {"customer_protocol": "1"}
    data = {
        "touchid_status": "not_supported",
        "jailbroken": False,
        "architecture": "arch64",
        "region": "US",
        "app_id": "com.duosecurity.duomobile",
        "full_disk_encryption": True,
        "passcode_status": True,
        "platform": "Android",
        "pkpush": "rsa-sha512",
        "pubkey": RSA.generate(2048).publickey().export_key().decode(),
        "app_version": "3.28.1",
        "app_build_number": 328104,
        "version": "9.0.0",
        "manufacturer": "Samsung",
        "language": "en",
        "model": "Samsung Smart Fridge",
        "security_patch_level": "2019-07-05",
    }

    address = f"https://{parsed.netloc}/push/v2/activation/{slug}"
    response = requests.post(address, headers=headers, params=params, data=data)
    response.raise_for_status()
    hotp_secret = response.json()["response"]["hotp_secret"]
    # Convert the raw secret (likely hexadecimal or another format) to Base32.
    # This ensures the secret works with pyotp.
    encoded_secret = base64.b32encode(hotp_secret.encode()).decode()
    return encoded_secret
