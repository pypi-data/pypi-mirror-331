import argparse
from purdue_connect.connection import connect_vpn, connect_ssh
from purdue_connect.otp import get_next_otp, set_hotp_secret_from_link, set_hotp_secret_from_qr
from purdue_connect.config import load_config, save_config

def check_update():
    import requests
    import pkg_resources

    package_name = "purdue-connect"
    installed_version = pkg_resources.get_distribution(package_name).version
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
    latest_version = response.json()["info"]["version"]

    if installed_version < latest_version:
        print(f"\033[1;31mA new version ({latest_version}) of {package_name} is available! Upgrade with:\033[0m")
        print(f"\033[1;32m pip install --upgrade {package_name} \033[0m")
    else:
        pass

if __name__ == "__main__":
    check_update()

def set_credentials(username, password):
    config = load_config()
    config["username"] = username
    config["password"] = password
    save_config(config)
    print("Credentials have been set successfully.")

def main():
    parser = argparse.ArgumentParser(description="Purdue Connect CLI Tool")
    
    check_update()

    # Mutually exclusive group for primary actions
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--vpn", action="store_true", help="Connect to Purdue VPN")
    group.add_argument("--ssh", metavar="SERVER", help="Connect to Purdue SSH server (e.g., ececomp.ecn.purdue.edu)")
    group.add_argument("--otp", action="store_true", help="Print a new OTP")
    group.add_argument("--set-secret-link", metavar="LINK", help="Set HOTP secret using an activation link")
    group.add_argument("--set-secret-qr", metavar="QR_URI", help="Set HOTP secret using a QR activation URI")
    group.add_argument("--set-credentials", nargs=2, metavar=("USERNAME", "PASSWORD"), help="Set permanent Purdue credentials")
    
    # Optional overrides for stored credentials
    parser.add_argument("--username", help="Purdue login username (overrides stored credential)")
    parser.add_argument("--password", help="Purdue base password (overrides stored credential)")
    
    args = parser.parse_args()

    if args.set_secret_link:
        set_hotp_secret_from_link(args.set_secret_link)
    elif args.set_secret_qr:
        set_hotp_secret_from_qr(args.set_secret_qr)
    elif args.set_credentials:
        username, password = args.set_credentials
        set_credentials(username, password)
    elif args.vpn:
        connect_vpn(username=args.username, password=args.password)
    elif args.ssh:
        connect_ssh(username=args.username, password=args.password, server=args.ssh)
    elif args.otp:
        try:
            otp = get_next_otp()
            print("Your OTP is:", otp)
        except Exception as e:
            print("Error generating OTP:", e)

if __name__ == "__main__":
    main()
