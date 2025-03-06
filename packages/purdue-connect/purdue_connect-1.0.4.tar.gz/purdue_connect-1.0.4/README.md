# Purdue Connect CLI

## Overview

**Purdue Connect** is a command-line tool that streamlines access to Purdue University’s network services by integrating Purdue’s two-factor authentication (BoilerKey/Duo) into your workflow. It allows you to securely store your Purdue credentials and HOTP secret (the secret used for generating one-time passcodes) so you can quickly generate One-Time Passwords (OTPs) and log in to Purdue VPN or SSH servers without manually retrieving codes each time.

## Features

- **HOTP Secret Management** – Set your BoilerKey/Duo HOTP secret using an activation URI or QR code.
- **One-Time Password (OTP) Generation** – Generate OTP codes from the CLI, eliminating the need to open the Duo app.
- **Persistent Credentials** – Store Purdue Career Account credentials securely for easier logins.
- **Purdue VPN Connection** – Connect to Purdue’s VPN using OpenConnect with an automatically generated OTP.
- **SSH to Purdue Servers** – SSH into Purdue’s remote servers with BoilerKey authentication automated.
- **Cross-Platform Support** – Works on Linux, macOS, and Windows (via WSL or compatible VPN clients).

## Installation

### Install from PyPI
```bash
pip install purdue-connect
```

### Verify Installation
```bash
purdue-connect --help
```

## Obtaining the Duo Mobile Activation Link (i.e. `<activation-link>`)
1. **Log in to a Purdue website** (e.g., [mypurdue.purdue.edu](https://mypurdue.purdue.edu)) and reach the BoilerKey login prompt.
2. **Click “Manage Devices”** (may be under "Other options" or a gear icon).
3. **Authenticate yourself** (Duo Push, bypass code, or existing device).
4. **Click “Add a new device”** and select **Tablet**.
5. **Copy the activation link** displayed below the QR code or via the “Email me an activation link” option.
6. **Use this link in Purdue Connect** during setup.

## Usage

### 1. Setting Up Your Credentials
```bash
purdue-connect --set-credentials <username> <password>
```
Enter your Purdue Career Account username and password.

### 2. Setting the HOTP Secret
```bash
purdue-connect --set-secret-link <activation-link>
```
Alternatively, use a QR URI:
```bash
purdue-connect --set-secret-qr <qr-uri>
```

### 3. Generating OTP Codes
```bash
purdue-connect --otp
```
Outputs a 6-digit one-time password to use with BoilerKey authentication.

### 4. Connecting to Purdue VPN
```bash
sudo purdue-connect --vpn
```

**Note:** After running `--vpn`, another terminal will open. However, the original terminal hosting the VPN connection will require you to enter your computer user password for it to start the VPN connection properly.

### 5. Connecting to Purdue SSH Servers
```bash
purdue-connect --ssh <hostname>
```
Example:
```bash
purdue-connect --ssh scholar.rcac.purdue.edu
```
Authenticates with your stored credentials and an automatic OTP.

**Hint:** You can use `--vpn` to connect to the Purdue VPN first, and then in the newly opened terminal, use `--ssh` to connect to servers that require Purdue VPN access, such as `ececomp`.

## Troubleshooting

### OpenConnect Not Found
Install OpenConnect:
```bash
# Ubuntu/Debian
sudo apt install openconnect

# Fedora
sudo dnf install openconnect

# macOS
brew install openconnect
```
For Windows, install **Cisco AnyConnect** from [webvpn.purdue.edu](https://webvpn.purdue.edu) or use **WSL**.

### SSH Connection Issues
- Ensure Purdue VPN is connected if required.
- Check stored credentials with `purdue-connect --set-credentials <username> <password>`.

### Invalid OTP or Wrong Code
- Ensure system clock is correct.
- If using HOTP, retry with a fresh OTP.
- Double-check your saved HOTP secret.

## License

Purdue Connect is a closed-source project. Redistribution, modification, and contributions are not allowed.