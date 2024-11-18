import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class LSDEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSD Editor")
        self.table_of_contents = []

        # Create the menu
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        json_menu = tk.Menu(menu, tearoff=0)
        json_menu.add_command(label="Serialise", command=self.json_serialise)
        json_menu.add_command(label="Deserialise", command=self.json_deserialise)

        menu.add_cascade(label="File", menu=file_menu)
        menu.add_cascade(label="JSON", menu=json_menu)
        self.root.config(menu=menu)

        # Create a frame for the Treeview and scrollbars
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("Main ID", "String ID", "Unlock ID"), show="headings")
        self.tree.heading("Main ID", text="Main ID")
        self.tree.heading("String ID", text="String ID")
        self.tree.heading("Unlock ID", text="Unlock ID")

        # Create vertical scrollbar
        tree_vscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=tree_vscroll.set)
        tree_vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        tree_hscroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscroll=tree_hscroll.set)
        tree_hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Pack the Treeview
        self.tree.pack(fill=tk.BOTH, expand=True)


        # Add buttons for table manipulation
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAT files", "*.dat")])
        if not file_path:
            return

        with open(file_path, "rb") as f:
            self.table_of_contents.clear()
            num_files = int.from_bytes(f.read(2), byteorder="little")
            for _ in range(num_files):
                main_id = int.from_bytes(f.read(2), byteorder="little")
                string_id = int.from_bytes(f.read(2), byteorder="little")
                unlock_id = int.from_bytes(f.read(2), byteorder="little")
                self.table_of_contents.append((main_id, string_id, unlock_id))

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for i, entry in enumerate(self.table_of_contents):
            self.tree.insert("", "end", values=(entry[0], entry[1], f"{entry[2]:X}"))

    def delete_entry(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No item selected.")
            return

        for item in selected_items:
            entry = self.tree.item(item)["values"]
            self.table_of_contents.remove((entry[0], entry[1], int(entry[2], 16)))
            self.tree.delete(item)

    def add_entry(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Entry")

        tk.Label(add_window, text="Main ID").grid(row=0, column=0)
        main_id_entry = tk.Entry(add_window)
        main_id_entry.grid(row=0, column=1)

        tk.Label(add_window, text="String ID").grid(row=1, column=0)
        string_id_entry = tk.Entry(add_window)
        string_id_entry.grid(row=1, column=1)

        tk.Label(add_window, text="Unlock ID (Hex)").grid(row=2, column=0)
        unlock_id_entry = tk.Entry(add_window)
        unlock_id_entry.grid(row=2, column=1)

        def add():
            try:
                main_id = int(main_id_entry.get())
                string_id = int(string_id_entry.get())
                unlock_id = int(unlock_id_entry.get(), 16)
                self.table_of_contents.append((main_id, string_id, unlock_id))
                self.populate_treeview()
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

        tk.Button(add_window, text="Add", command=add).grid(row=3, columnspan=2)

    def json_serialise(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        # Load the JSON file
        with open(file_path, "r") as f:
            data = json.load(f)

        # Validate the JSON structure
        if "header" not in data or "LSD" not in data:
            messagebox.showerror("Error", "Invalid JSON format.")
            return

        # Populate the table_of_contents
        self.table_of_contents = []
        for item in data["LSD"].values():
            self.table_of_contents.append((item["asset_id"], item["string_id"], item["unlock_id"]))

        # Save as binary
        save_path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("DAT files", "*.dat")])
        if not save_path:
            return

        # Convert data to binary format and save
        binary_data = len(self.table_of_contents).to_bytes(2, byteorder="little")
        for entry in self.table_of_contents:
            binary_data += entry[0].to_bytes(2, byteorder="little")
            binary_data += entry[1].to_bytes(2, byteorder="little")
            binary_data += entry[2].to_bytes(2, byteorder="little")

        with open(save_path, "wb") as f:
            f.write(binary_data)

        messagebox.showinfo("Success", f"JSON file serialized and saved as binary at {save_path}")

        # Update the TreeView for user feedback
        self.populate_treeview()


    def json_deserialise(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        json_data = {
            "header": "SVR06",
            "LSD": {
                f"Item {i}": {
                    "asset_id": entry[0],
                    "string_id": entry[1],
                    "unlock_id": entry[2]
                }
                for i, entry in enumerate(self.table_of_contents)
            }
        }

        with open(file_path, "w") as f:
            json.dump(json_data, f, indent=4)

        messagebox.showinfo("Success", f"Table of contents serialized to {file_path}")

    def save(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("DAT files", "*.dat")])
        if not file_path:
            return

        data = len(self.table_of_contents).to_bytes(2, byteorder="little")
        for entry in self.table_of_contents:
            data += entry[0].to_bytes(2, byteorder="little")
            data += entry[1].to_bytes(2, byteorder="little")
            data += entry[2].to_bytes(2, byteorder="little")

        with open(file_path, "wb") as f:
            f.write(data)

        messagebox.showinfo("Success", f"Binary file saved to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LSDEditorApp(root)
    root.resizable(True, True)
    # Grab width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size to 80% of screen size
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)

    root.geometry(f"{window_width}x{window_height}")

    root.mainloop()
