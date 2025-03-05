# Purdue Connect

Purdue Connect is a cross-platform command-line tool that connects to Purdue VPN and SSH servers using HOTP-based OTPs. It integrates an internal HOTP activation module to extract the HOTP secret from an activation URI (provided as a link or a QR activation URI), so no external dependency is required for secret extraction.

## Features

- **Set HOTP Secret:**  
  Extract and set the HOTP secret using an activation URI. Use either a direct activation link or a QR-style activation URI.

- **Generate OTP:**  
  OTPs are generated using the HOTP algorithm. The OTP counter is stored persistently so each OTP is unique.

- **Persistent Credentials:**  
  Permanently store your Purdue username and base password for convenience.

- **VPN and SSH Connection:**  
  Use the generated OTP (combined with your base password) to authenticate with Purdue VPN (`webvpn2.purdue.edu`) or SSH servers.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/purdue-connect.git
   cd purdue-connect
