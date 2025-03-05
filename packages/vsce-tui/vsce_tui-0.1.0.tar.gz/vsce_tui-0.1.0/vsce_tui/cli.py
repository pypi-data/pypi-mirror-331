# vsce-ext-manager.py (working name)

import csv
import subprocess
import os
import sys
import termios
import tty
import json

# --- Configuration ---
# CSV_FILE is now dynamically generated in get_current_profile()

# ANSI escape codes for color
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# --- Data Model ---
def load_extensions():
    """Loads extensions from the CSV file or creates it if it doesn't exist."""
    extensions = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                extensions.append(row)
        # Get current extensions and add any new ones
        current_ext_list = subprocess.check_output(
            "code-insiders --list-extensions", shell=True, text=True
        ).strip()
        current_ext_ids = [line for line in current_ext_list.split('\n') if "." in line]
        existing_ext_ids = [ext['extension_id'] for ext in extensions]
        for ext_id in current_ext_ids:
            if ext_id not in existing_ext_ids:
                extensions.append({'extension_id': ext_id, 'status': 'Installed', 'changed': False})
        save_extensions(extensions) # Save any new extensions
    else:
        # Get extensions from stdin (piped from `code --list-extensions`)
        ext_list_output = subprocess.check_output(
            "code-insiders --list-extensions", shell=True, text=True  # Use code-insiders
        ).strip()

        for line in ext_list_output.split('\n'):
            if "." in line:  # Skip lines that don't look like extension IDs
                extensions.append({'extension_id': line, 'status': 'Installed', 'changed': False})

        save_extensions(extensions) # Save to create initial file
    return extensions

def save_extensions(extensions):
    """Saves the extensions to the CSV file."""
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['extension_id', 'status', 'changed']  # Include 'changed'
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extensions)

def clean_extensions():
    """Refreshes the list of extensions in the CSV file."""
    extensions = []
    ext_list_output = subprocess.check_output(
        "code-insiders --list-extensions", shell=True, text=True
    ).strip()

    for line in ext_list_output.split('\n'):
        if "." in line:
            extensions.append({'extension_id': line, 'status': 'Installed', 'changed': False})
    save_extensions(extensions)
    print("Extension list cleaned and refreshed.")

# --- TUI ---
def getch():
    """Reads a single character from stdin without echoing to the screen."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def display_tui(extensions):
    """Displays the text-based UI and handles user input."""
    current_index = 0
    viewport_start = 0
    terminal_height = os.get_terminal_size().lines
    viewport_size = terminal_height - 3  # Leave space for header and prompt

    if sys.stdin.isatty():  # Interactive mode
        while True:
            # Clear the screen (cross-platform)
            os.system('cls' if os.name == 'nt' else 'clear')

            print("VS Code Extension Manager (Press 't' or 'Space' to toggle, 'q' to quit and apply, 'x' to quit without applying, 'w' to apply)")

            # Display only the extensions within the viewport
            for i in range(viewport_start, min(viewport_start + viewport_size, len(extensions))):
                ext = extensions[i]
                status_char = f"{GREEN}✓{RESET}" if ext['status'] == 'Installed' else f"{RED}✗{RESET}"  # Unicode checkmark/X with color
                marker = ">" if i == current_index else " "
                print(f"{marker} {status_char} {ext['extension_id']}") # No brackets

            key = getch().lower()

            if key == 'q':
                apply_changes(extensions)  # Apply changes before quitting
                break
            elif key == 'x':
                break  # Quit without applying changes
            elif key == 'w':
                apply_changes(extensions)  # Apply changes
            elif key == 't' or key == ' ':  # Toggle on 't' or Spacebar
                if extensions[current_index]['status'] == 'Installed':
                    extensions[current_index]['status'] = 'Uninstalled'
                else:
                    extensions[current_index]['status'] = 'Installed'
                extensions[current_index]['changed'] = True  # Mark as changed
            elif key == 'j': # Down
                current_index = min(current_index + 1, len(extensions) - 1)
                # Adjust viewport if necessary
                if current_index >= viewport_start + viewport_size:
                    viewport_start += 1
            elif key == 'k': # Up
                current_index = max(current_index - 1, 0)
                # Adjust viewport if necessary
                if current_index < viewport_start:
                    viewport_start -= 1
            elif key == '\x1b':  # Escape sequence (for arrow keys)
                next_char = getch()
                if next_char == '[':
                    third_char = getch()
                    if third_char == 'A':  # Up arrow
                        current_index = max(current_index - 1, 0)
                        if current_index < viewport_start:
                            viewport_start -= 1
                    elif third_char == 'B':  # Down arrow
                        current_index = min(current_index + 1, len(extensions) - 1)
                        if current_index >= viewport_start + viewport_size:
                            viewport_start += 1
                    # Ignore right/left arrows (C and D)

    else:  # Piped input mode - just display once
        print("VS Code Extension Manager (Extensions loaded from pipe)")
        for i, ext in enumerate(extensions):
            status_char = "✓" if ext['status'] == 'Installed' else "✗"  # Unicode checkmark/X
            print(f"  [{status_char}] {ext['extension_id']}")
        print("Changes will be applied when you run the script interactively.")


# --- VS Code Interaction ---
def apply_changes(extensions):
    """Applies the changes (install/uninstall) to VS Code."""

    current_ext_list = subprocess.check_output(
        "code-insiders --list-extensions", shell=True, text=True
    ).strip()
    current_ext_ids = [line for line in current_ext_list.split('\n') if "." in line]

    for ext in extensions:
        if ext['changed']:  # Only process changed extensions
            if ext['status'] == 'Installed':
                if ext['extension_id'] not in current_ext_ids:  # Only install if not already installed
                    print(f"Installing {ext['extension_id']}...")
                    subprocess.run(['code-insiders', '--install-extension', ext['extension_id']], check=False) # Use code-insiders
            #  Do nothing if status is 'Uninstalled' - just keep it in the CSV

def get_user_data_dir():
    """Gets the VS Code user data directory based on the OS."""
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'Code - Insiders')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/Code - Insiders')
    else:  # Linux
        return os.path.expanduser('~/.config/Code - Insiders')

def get_current_profile():
    """Gets the current VS Code profile name from argv.json."""
    user_data_dir = get_user_data_dir()
    argv_path = os.path.join(user_data_dir, 'argv.json')
    try:
        with open(argv_path, 'r') as f:
            argv = json.load(f)
            return argv.get('profile-name', 'Default')  # Default profile name
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 'Default'

# --- Main ---
CONFIG_DIR = os.path.expanduser("~/.config/vsce_tui")
CSV_FILE = os.path.join(CONFIG_DIR, f"vsce-ext-manager_{get_current_profile()}.csv")

def main():
    """Main function."""
    # Create the config directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean_extensions()
    else:
        extensions = load_extensions()
        display_tui(extensions)
        save_extensions(extensions) # Always save, even if no changes are applied
    # apply_changes(extensions) is now called within display_tui when 'q' is pressed

if __name__ == "__main__":
    main()