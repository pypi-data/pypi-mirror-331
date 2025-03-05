import sys
import time
import select
import subprocess
import platform
import warnings
from .otp import get_next_otp
from .config import load_config

def get_credentials():
    """
    Returns the stored username and base password.
    """
    config = load_config()
    return config.get("username"), config.get("password")

def build_combined_password(password):
    """
    Combines the stored base password with a freshly generated OTP.
    
    The old bash script used a base password ending with a comma
    (e.g. "Umby2006!PUR,"). This function ensures that a comma is appended
    if not already present, then concatenates the OTP.
    
    Adjust the separator if needed.
    """
    otp = get_next_otp()
    if not password.endswith(','):
        password += ','
    return f"{password}{otp}"

def connect_vpn(username=None, password=None):
    """
    Connects to Purdue VPN (webvpn2.purdue.edu) using stored credentials and
    the combined password (base password + OTP). The OpenConnect process runs
    in the background with its output hidden. Meanwhile, a new blank terminal
    is opened for the user to perform other tasks.
    
    The current terminal displays a minimal header ("VPN CONNECTED" in green)
    and remains active until Ctrl+C is pressed to disconnect the VPN.
    """
    # Use provided credentials or fall back on stored ones.
    if username is None or password is None:
        stored_username, stored_password = get_credentials()
        if stored_username is None or stored_password is None:
            print("No credentials provided or stored. Please set your credentials.")
            return
        username, password = stored_username, stored_password

    combined = build_combined_password(password)
    # Build the OpenConnect command.
    cmd = ["sudo", "openconnect", "--user", username, "--passwd-on-stdin", "webvpn2.purdue.edu"]
    print("Connecting to Purdue VPN...")

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        # Send the combined password (with a newline) to OpenConnect.
        proc.stdin.write(combined + "\n")
        proc.stdin.flush()
    except FileNotFoundError:
        print("\033[31mError: OpenConnect command not found. Please install OpenConnect.\033[0m")
        return
    except Exception as e:
        print(f"\033[31mError launching VPN: {e}\033[0m")
        return

    # Open a new blank terminal window for the user.
    try:
        system = platform.system()
        if system == "Windows":
            # Opens a new Command Prompt window.
            subprocess.Popen('start cmd.exe', shell=True)
        elif system == "Darwin":  # macOS
            # Uses AppleScript to open a new Terminal window with the default shell.
            apple_script = 'tell application "Terminal" to do script ""'
            subprocess.Popen(["osascript", "-e", apple_script])
        elif system == "Linux":
            # Try common terminal emulators.
            try:
                subprocess.Popen(["gnome-terminal"])
            except FileNotFoundError:
                try:
                    subprocess.Popen(["konsole"])
                except FileNotFoundError:
                    try:
                        subprocess.Popen(["xterm"])
                    except FileNotFoundError:
                        print("No supported terminal emulator found. Please install gnome-terminal, konsole, or xterm.")
            else:
                pass
        else:
            print("Unsupported operating system for opening a new terminal.")
    except Exception as e:
        print(f"Error opening new terminal: {e}")

    # Clear the terminal and display the minimal header.
    print("\033[2J\033[H", end="")  # Clear screen and move cursor to top.
    print("\033[1;32mVPN CONNECTED\033[0m")  # Bold green header.
    print("Press ^C to disconnect.\n")

    try:
        # Wait until the OpenConnect process terminates or until Ctrl+C is pressed.
        while proc.poll() is None:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDisconnecting VPN...")
        proc.terminate()
        proc.wait()
        print("VPN disconnected.")

def connect_ssh(server, username=None, password=None):
    """
    Connects to a Purdue SSH server using stored credentials and the combined password.
    
    This function requires the SSH server to be provided (e.g. ececomp.ecn.purdue.edu).
    It uses Paramiko to establish an interactive SSH session.
    
    This version suppresses cryptography deprecation warnings and directly streams
    the SSH channel output to the user's terminal, so that the remote prompt remains
    on the same line as the user's input.
    """
    if not server:
        print("SSH server must be provided.")
        return

    if username is None or password is None:
        stored_username, stored_password = get_credentials()
        if stored_username is None or stored_password is None:
            print("No credentials provided or stored. Please set your credentials.")
            return
        username, password = stored_username, stored_password

    # Suppress cryptography deprecation warnings.
    try:
        from cryptography.utils import CryptographyDeprecationWarning
        import warnings
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
    except ImportError:
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    try:
        import paramiko, socket, termios, tty
    except ImportError:
        print("Paramiko is not installed. Please install it (pip install paramiko) to use SSH functionality.")
        return

    combined = build_combined_password(password)
    print("Connecting to SSH server...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server, username=username, password=combined)
    except Exception as e:
        print(f"SSH connection failed: {e}")
        return

    channel = client.invoke_shell()
    print("SSH connection established. Type commands below (press Ctrl+C to exit).")

    # Save terminal settings.
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        channel.settimeout(0.0)
        while True:
            r, _, _ = select.select([channel, sys.stdin], [], [])
            if channel in r:
                try:
                    data = channel.recv(1024)
                    if len(data) == 0:
                        break
                    # Write data directly without splitting lines.
                    sys.stdout.write(data.decode())
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if not x:
                    break
                channel.send(x)
    except KeyboardInterrupt:
        print("\nExiting SSH session...")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        client.close()
