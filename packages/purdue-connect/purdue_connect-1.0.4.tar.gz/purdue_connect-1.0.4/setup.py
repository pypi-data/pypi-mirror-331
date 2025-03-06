import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        # Run the standard install process first.
        install.run(self)
        # Check if OpenConnect is installed.
        try:
            subprocess.check_call(
                ["openconnect", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("OpenConnect is already installed.")
        except FileNotFoundError:
            print("OpenConnect not found. Attempting to install OpenConnect automatically...")
            if sys.platform.startswith("linux"):
                try:
                    # This example uses apt-get for Debian/Ubuntu systems.
                    subprocess.check_call(["sudo", "apt-get", "update"])
                    subprocess.check_call(["sudo", "apt-get", "install", "-y", "openconnect"])
                    print("OpenConnect installed successfully.")
                except Exception as e:
                    print("Automatic installation of OpenConnect failed. Please install it manually.")
            elif sys.platform.startswith("darwin"):
                try:
                    # Attempt to use Homebrew on macOS.
                    subprocess.check_call(["brew", "install", "openconnect"])
                    print("OpenConnect installed successfully.")
                except Exception as e:
                    print("Automatic installation of OpenConnect failed. Please install it manually.")
            elif sys.platform.startswith("win"):
                print("Automatic installation is not supported on Windows. Please install OpenConnect manually.")
            else:
                print("Unsupported OS for automatic installation of OpenConnect. Please install it manually.")

setup(
    name="purdue-connect",
    version="1.0.4",
    packages=find_packages(),
    install_requires=[
        "pyotp",
        "qrcode",
        "pycryptodome",  # Provides Crypto.PublicKey; ensure to install pycryptodome
        "requests",
        "paramiko",      # Added Paramiko dependency for SSH functionality
    ],
    entry_points={
        "console_scripts": [
            "purdue-connect=purdue_connect.cli:main"
        ]
    },
    author="Umberto Maria Puddu",
    author_email="upuddu@purdue.edu",
    description="Command line tool for Purdue VPN and SSH connections using HOTP-based OTP",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    cmdclass={'install': CustomInstall},
)
