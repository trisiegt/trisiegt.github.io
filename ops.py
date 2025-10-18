# ======================================
#      Minecraft Operator Manager
#  Programmed by justTrisie, urs truly!
# ======================================
import json
import os
import re
import urllib.request
from urllib.error import HTTPError
import ssl

# --- ANSI Color Codes ---
class AnsiColors:
    RESET = "\u001b[0m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"

# --- Obfuscated Target String and Decryption Logic ---
NOTSEEINGTHIS = 77
just_another_variable = [39, 56, 62, 57, 25, 63, 36, 62, 36, 40]

def _dcrt(obf_bytes, key):
    """Simple XOR decryption of a byte list into a string."""
    return "".join(chr(b ^ key) for b in obf_bytes)

# --- Renamed Rainbow Helper ---
def _rdr(text):
    # Cycle through the colors for a rainbow effect
    RAINBOW = [AnsiColors.RED, AnsiColors.YELLOW, AnsiColors.GREEN, AnsiColors.CYAN, AnsiColors.BLUE, AnsiColors.MAGENTA]
    result = ""
    for i, char in enumerate(text):
        color = RAINBOW[i % len(RAINBOW)]
        # Do NOT include RESET here, it's handled by the outer colorize function
        result += f"{color}{char}"
    return result

# --- Text Coloring Helpers ---
def colorize(text, color_code):
    return f"{color_code}{text}{AnsiColors.RESET}"

# --- File Configuration ---
OPS_FILE = "ops.json"

# ---------------- Helper Functions ----------------

def get_uuid_from_name(username):
    """
    Fetches the UUID for a Minecraft username using the Mojang API.
    Returns the UUID string or None if not found or an error occurs.
    """
    # Minecraft UUID API endpoint
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    
    # Create an unverified SSL context to handle potential cert issues on some systems
    # Using default context is more secure, but this is a common fix for simple requests
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(url, context=ssl_context) as response:
            # Mojang API returns 204 No Content for a non-existent user
            if response.status == 204:
                print(colorize(f"🚫 Error: Username '{username}' does not exist on Mojang servers.", AnsiColors.RED))
                return None
            
            # Read and decode the JSON response
            data = json.loads(response.read().decode())
            # The UUID from Mojang is a 32-character string without hyphens, 
            # but ops.json requires the standard hyphenated format (8-4-4-4-12).
            uuid_no_hyphens = data.get("id", "")
            
            # Format the UUID with hyphens: 8-4-4-4-12
            formatted_uuid = (
                uuid_no_hyphens[:8] + "-" + 
                uuid_no_hyphens[8:12] + "-" + 
                uuid_no_hyphens[12:16] + "-" + 
                uuid_no_hyphens[16:20] + "-" + 
                uuid_no_hyphens[20:]
            )
            return formatted_uuid
            
    except HTTPError as e:
        print(colorize(f"🚫 HTTP Error fetching UUID for {username}: {e.code} {e.reason}", AnsiColors.RED))
        return None
    except Exception as e:
        print(colorize(f"🚫 An unexpected error occurred: {e}", AnsiColors.RED))
        return None


def load_ops(file_path=OPS_FILE):
    if not os.path.exists(file_path):
        print(colorize(f"Error: {file_path} not found!", AnsiColors.RED))
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        # Remove trailing commas
        content = re.sub(r",\s*]", "]", content)
        content = re.sub(r",\s*}", "}", content)

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(colorize(f"JSON parsing error: {e}", AnsiColors.RED))
            print(colorize("Make sure your ops.json is properly formatted.", AnsiColors.YELLOW))
            return []

def save_ops(ops, file_path=OPS_FILE):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(ops, f, indent=4)
    print(colorize(f"\n✅ Saved {len(ops)} ops to {file_path}!\n", AnsiColors.GREEN))

def explain_level(level):
    explanations = {
        1: "Level 1: Can bypass spawn protection",
        2: "Level 2: Can use /clear, /difficulty, /effect, /gamemode, /gamerule, /give, /tp, /spawnpoint",
        3: "Level 3: Can use /ban, /deop, /kick, /op, /stop, /whitelist, and all lower level commands",
        4: "Level 4: Full control, all commands available"
    }
    return explanations.get(level, "Unknown level")

# ---------------- Core Functions ----------------

def list_ops(ops):
    if not ops:
        print("No ops found.")
        return
    
    # FIX: Using the variables you supplied (just_another_variable and NOTSEEINGTHIS)
    target_name = _dcrt(just_another_variable, NOTSEEINGTHIS)

    print(colorize("\nCurrent Ops:", AnsiColors.GREEN))
    for i, op in enumerate(ops, 1):
        op_name = op.get('name','<unknown>')
        op_level = op.get('level','?')
        op_uuid = op.get('uuid', '')

        # Check for the decrypted name and apply rainbow effect
        if op_name == target_name:
            display_name = _rdr(op_name)
        else:
            display_name = op_name
        
        # Determine UUID display
        uuid_display = colorize(op_uuid if op_uuid else "OFFLINE/CRACKED UUID", AnsiColors.BLUE)
            
        line = f"{i}. {display_name} - Level {op_level} ({uuid_display})"
        
        # Colorize the whole line MAGENTA (rainbow codes will override where needed)
        print(colorize(line, AnsiColors.MAGENTA))

def add_op(ops, file_path=OPS_FILE):
    name = input(colorize("Enter Minecraft username: ", AnsiColors.YELLOW)).strip()
    if not name:
        print("No name entered. Cancelling...")
        return
    
    # --- UUID Lookup and Cracked Mode ---
    print(colorize("\n--- UUID Lookup ---", AnsiColors.CYAN))
    print(colorize("Note: Minecraft servers running in **online-mode=true** need a real UUID.", AnsiColors.CYAN))
    print(colorize("If your server is **cracked (online-mode=false)**, the UUID should be blank.", AnsiColors.CYAN))

    uuid_choice = input(colorize(f"Look up UUID for '{name}'? (y/n/c for cracked): ", AnsiColors.YELLOW)).strip().lower()
    
    op_uuid = ""
    if uuid_choice == 'y':
        print(colorize("Searching Mojang API...", AnsiColors.CYAN))
        op_uuid = get_uuid_from_name(name)
        if op_uuid is None:
            # If lookup fails, prompt the user if they want to proceed without it (maybe an API error)
            proceed = input(colorize("UUID lookup failed. Proceed with blank UUID (for cracked server)? (y/n): ", AnsiColors.RED)).strip().lower()
            if proceed != 'y':
                print(colorize("Operation cancelled.", AnsiColors.RED))
                return
            else:
                op_uuid = ""
        else:
            print(colorize(f"✅ Found UUID: {op_uuid}", AnsiColors.GREEN))
    elif uuid_choice == 'c':
        print(colorize("Using blank UUID for Cracked/Offline mode.", AnsiColors.YELLOW))
        op_uuid = ""
    elif uuid_choice == 'n':
        custom_uuid = input(colorize("Enter custom UUID (or leave blank for cracked): ", AnsiColors.YELLOW)).strip()
        op_uuid = custom_uuid
    else:
        print(colorize("Invalid choice. Cancelling...", AnsiColors.RED))
        return
        
    # --- OP Level Selection ---
    while True:
        try:
            level_input = input(colorize("\nEnter OP level (1-4): ", AnsiColors.YELLOW))
            level = int(level_input)
            if level not in [1, 2, 3, 4]:
                print(colorize("Invalid level! Must be 1-4.", AnsiColors.YELLOW))
                continue
            break
        except ValueError:
            print(colorize("Please enter a number between 1 and 4.", AnsiColors.YELLOW))
            
    print(f"Explanation: {explain_level(level)}")
    
    # Add to ops list
    ops.append({"uuid": op_uuid, "name": name, "level": level, "bypassesPlayerLimit": False})
    save_ops(ops, file_path)

def remove_op(ops, file_path=OPS_FILE):
    list_ops(ops)
    if not ops:
        return
    try:
        index_input = input(colorize("Enter the number of the OP to remove: ", AnsiColors.YELLOW))
        index = int(index_input)
        if 1 <= index <= len(ops):
            removed = ops.pop(index-1)
            print(colorize(f"Removed {removed.get('name','<unknown>')} successfully.", AnsiColors.GREEN))
            save_ops(ops, file_path)
        else:
            print(colorize("Invalid number!", AnsiColors.YELLOW))
    except ValueError:
        print(colorize("Please enter a valid number!", AnsiColors.YELLOW))

def select_file():
    global OPS_FILE
    path = input(colorize("Enter path to ops.json (leave empty for default './ops.json'): ", AnsiColors.YELLOW)).strip()
    if path:
        OPS_FILE = path
    print(f"Using ops file: {OPS_FILE}")

# ---------------- Main Menu ----------------

def main():
    select_file()
    ops = load_ops(OPS_FILE)
    while True:
        print(colorize("\n=== Minecraft OP Manager ===", AnsiColors.CYAN))
        print(colorize("1. List all ops", AnsiColors.CYAN))
        print(colorize("2. Add an op", AnsiColors.CYAN))
        print(colorize("3. Remove an op", AnsiColors.CYAN))
        print(colorize("4. Reload ops.json", AnsiColors.CYAN))
        print(colorize("5. Quit", AnsiColors.CYAN))
        choice = input(colorize("Choose an option: ", AnsiColors.YELLOW)).strip()
        
        if choice == "1":
            list_ops(ops)
        elif choice == "2":
            add_op(ops, OPS_FILE)
        elif choice == "3":
            remove_op(ops, OPS_FILE)
        elif choice == "4":
            ops = load_ops(OPS_FILE)
            print(colorize("Reloaded ops.json", AnsiColors.GREEN))
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print(colorize("Invalid choice, try again.", AnsiColors.YELLOW))

if __name__ == "__main__":
    # Enable ANSI escape codes on Windows console if possible
    if os.name == 'nt':
        os.system('') 
    main()
