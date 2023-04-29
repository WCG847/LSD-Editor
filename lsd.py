import os
import tkinter as tk
from tkinter import filedialog

# Prompt user to select a dat file
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("DAT files", "*.dat")])

# Read contents of the file
with open(file_path, "rb") as f:
    num_files = int.from_bytes(f.read(2), byteorder="little")
    table_of_contents = []
    for i in range(num_files):
        main_id = int.from_bytes(f.read(2), byteorder="little")
        string_id = int.from_bytes(f.read(2), byteorder="little")
        unlock_id = int.from_bytes(f.read(2), byteorder="little")
        table_of_contents.append((main_id, string_id, unlock_id))

# Display table of contents
print("Table of Contents:")
for i, entry in enumerate(table_of_contents):
    print(f"{i+1}. Main ID: {entry[0]}, String ID: {entry[1]}, Unlock ID: {entry[2]:X}")

# Ask user to choose an action
while True:
    choice = input("Select an action (1 = delete entry, 2 = add entry, 3 = dump table of contents): ")
    if choice not in ["1", "2", "3"]:
        print("Invalid choice. Please select 1, 2, or 3.")
        continue
    break

if choice == "1":
    # Ask user which entry to delete
    while True:
        entry_nums = input("Enter the numbers of the entries to delete (comma-separated): ")
        try:
            entry_nums = [int(x.strip()) for x in entry_nums.split(",")]
            if not all(1 <= num <= len(table_of_contents) for num in entry_nums):
                raise ValueError()
        except ValueError:
            print("Invalid entry numbers. Please enter comma-separated numbers between 1 and", len(table_of_contents))
            continue
        break
    
    # Delete selected entries from table of contents
    table_of_contents = [entry for i, entry in enumerate(table_of_contents) if i+1 not in entry_nums]

elif choice == "2":
    # Ask user for new entry information
    main_id = int(input("Enter main ID: "))
    string_id = int(input("Enter string ID: "))
    unlock_id = int(input("Enter unlock ID (in hex format): "), 16)
    
    # Add new entry to table of contents
    table_of_contents.append((main_id, string_id, unlock_id))

elif choice == "3":
    # Dump table of contents to LSD folder
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    lsd_folder = os.path.join(desktop_path, "LSD")
    if not os.path.exists(lsd_folder):
        os.mkdir(lsd_folder)
    lsd_file = os.path.join(lsd_folder, "Dump_lsd.txt")
    with open(lsd_file, "w") as f:
        f.write("Table of Contents:\n")
        for i, entry in enumerate(table_of_contents):
            f.write(f"{i+1}. Main ID: {entry[0]}, String ID: {entry[1]}, Unlock ID: {entry[2]:X}\n")
    print(f"Table of contents dumped to {lsd_file}")

# Update 0x00 and 0x01 to reflect new number of files
num_files = len(table_of_contents)
data = num_files.to_bytes(2, byteorder="little")

# Update file contents with modified table of contents
for entry in table_of_contents:
    data += entry[0].to_bytes(2, byteorder="little")
    data += entry[1].to_bytes(2, byteorder="little")
    data += entry[2].to_bytes(2, byteorder="little")

# Save modified file to LSD folder on desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
lsd_folder = os.path.join(desktop_path, "LSD")
if not os.path.exists(lsd_folder):
    os.mkdir(lsd_folder)
lsd_file = os.path.join(lsd_folder, "file.lsd")
with open(lsd_file, "wb") as f:
    f.write(data)
print("File is saved! Check LSD folder on your desktop.")

