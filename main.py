import yapbol
import re
import difflib
import tkinter as tk
from tkinter import filedialog


def write_asciiz(f, string):
    if isinstance(string, bytes):
        f.write(string)
    else:
        f.write(string.encode('utf-8'))

    f.write(b'\0')


# Monkey patching yapbol to fix writing binary data
yapbol.pbo.write_asciiz = write_asciiz


def select_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select PBO File", filetypes=[("PBO files", "*.pbo")])

    return file_path


def main():
    pbo_file_path = select_file()

    if not pbo_file_path:
        print("No file selected. Exiting.")
        return

    print(f"Reading file: {pbo_file_path}")
    pbo = yapbol.PBOFile.read_file(pbo_file_path)
    print("File read successfully.")
    print("Searching for mission.sqm file.")
    try:
        mission_file = pbo['mission.sqm']
    except KeyError:
        print("No mission.sqm file found in the PBO file. Exiting.")
        return
    print("mission.sqm file found, reading data.")
    mission = mission_file.data.decode('utf-8')

    print("Looking for addons section in mission.sqm file.")
    addons = re.search(r'addons\[]=\s*{([^}]*)};?', mission, re.IGNORECASE)
    if addons:
        print("Addons section found.")
        addons_content = addons.group(1)
        print("Removing cup ace compat addons.")
        addons_content = re.sub(
            r'^\s*"[^"]*?(?=.*cup)(?=.*compat)(?=.*ace)[^"]*?",?(\r\n|\r|\n)',
            '',
            addons_content,
            flags=re.IGNORECASE | re.MULTILINE
        )

        mission2 = re.sub(
            r'(addons\[]=\s*{)([^}]*)(};?)',
            r'\1' + addons_content + r'\3',
            mission,
            flags=re.IGNORECASE | re.MULTILINE
        )

        print("Diff of the changes:")
        diff = difflib.unified_diff(mission.splitlines(), mission2.splitlines(), lineterm='')
        print('\n'.join(diff))

        print("Saving the fixed mission.sqm file.")
        pbo['mission.sqm'].data = mission2.encode('utf-8')
        new_pbo_file_path = pbo_file_path.replace(".pbo", "(Fixed).pbo")
        pbo.save_file(new_pbo_file_path)
        print(f"Fixed PBO file saved as: {new_pbo_file_path}")
    else:
        print("No cup compat ace addons found in the mission.sqm file.")

    print("Exiting.")
    input("Press Enter to exit.")


if __name__ == "__main__":
    main()
