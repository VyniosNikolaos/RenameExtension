"""
RenameExtension.py

A utility to recursively find all files with a given extension under
a specified directory and rename them to a new extension. Handles
case-insensitive filesystems and provides a simple Tkinter GUI for
user input.

Key design considerations:
 - Bottom-up traversal prevents confusion when scanning renamed files.
 - Provides feedback on skipped collisions when target name exists.
 - GUI fields for directory path, old extension, and new extension.
"""
import os
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox


def normalize_ext(ext: str) -> str:
    """
    Ensure the extension starts with a dot and is lowercase.
    """
    ext = ext.strip().lower()
    return ext if ext.startswith('.') else '.' + ext


def safe_rename(old_path: str, new_path: str):
    """Robust rename on case-insensitive filesystems."""
    if os.path.normcase(old_path) == os.path.normcase(new_path):
        # Two-step rename via UUID
        dirpath = os.path.dirname(old_path)
        temp = os.path.join(dirpath, str(uuid.uuid4()))
        os.rename(old_path, temp)
        os.rename(temp, new_path)
    else:
        os.rename(old_path, new_path)


def rename_extensions(path: str, old_ext: str, new_ext: str):
    """
    Walk the directory tree bottom-up, renaming files that end with old_ext
    to end with new_ext.
    """
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")

    old_ext = normalize_ext(old_ext)
    new_ext = normalize_ext(new_ext)

    for root, dirs, files in os.walk(path, topdown=False):
        for fname in files:
            if fname.lower().endswith(old_ext):
                base = fname[:-len(old_ext)]
                new_name = base + new_ext
                old_path = os.path.join(root, fname)
                new_path = os.path.join(root, new_name)

                if os.path.exists(new_path) and not os.path.normcase(old_path) == os.path.normcase(new_path):
                    print(f"[WARN] Skipping {old_path}: target exists")
                else:
                    safe_rename(old_path, new_path)


def browse_dir():
    sel = filedialog.askdirectory()
    if sel:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, sel)


def run():
    path = entry_path.get().strip()
    old_ext = entry_old.get().strip()
    new_ext = entry_new.get().strip()

    if not path or not old_ext or not new_ext:
        messagebox.showerror("Error", "All fields must be filled out.")
        return
    try:
        rename_extensions(path, old_ext, new_ext)
        messagebox.showinfo("Done", f"Renamed *{old_ext} to *{new_ext} in:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI setup ---
root = tk.Tk()
root.title("Batch Extension Renamer")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Directory
tk.Label(frame, text="Directory:").grid(row=0, column=0, sticky="w")
entry_path = tk.Entry(frame, width=40)
entry_path.grid(row=0, column=1)
browse_btn = tk.Button(frame, text="Browse...", command=browse_dir)
browse_btn.grid(row=0, column=2, padx=5)

# Old extension
tk.Label(frame, text="Old Ext:").grid(row=1, column=0, sticky="w")
entry_old = tk.Entry(frame, width=10)
entry_old.grid(row=1, column=1, sticky="w")

# New extension
tk.Label(frame, text="New Ext:").grid(row=2, column=0, sticky="w")
entry_new = tk.Entry(frame, width=10)
entry_new.grid(row=2, column=1, sticky="w")

# Run button
run_btn = tk.Button(frame, text="Rename", width=10, command=run)
run_btn.grid(row=3, column=1, pady=10)

root.mainloop()

# To build an executable with PyInstaller:
# 1. Install: pip install pyinstaller
# 2. Run: pyinstaller --onefile --windowed RenameExtension.py
#    - --onefile bundles into a single exe
#    - --windowed hides the console on Windows