import tkinter as tk
from tkinter import filedialog, messagebox
import json
import subprocess
import os

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Dashboard")
        self.maps = []
        self.listbox = tk.Listbox(root, width=50)
        self.listbox.pack(padx=10, pady=10)
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Add Map", command=self.add_map).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Open Map", command=self.open_map).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side=tk.LEFT)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.maps = []
        for file in os.listdir('.'):
            if file.endswith('.json'):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    img = data.get('image', 'image.png')
                    pts = len(data.get('points', []))
                    last_score = data.get('last_score')
                    score_str = f" | Last Score: {last_score}" if last_score is not None else ""
                    self.listbox.insert(tk.END, f"{file} | {img} | {pts} points{score_str}")
                    self.maps.append(file)
                except Exception:
                    continue

    def add_map(self):
        # Launch prototype.p
        subprocess.Popen(['python', 'prototype.py'])

    def open_map(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a map to open.")
            return
        map_file = self.maps[sel[0]]
        subprocess.Popen(['python', 'prototype.py', map_file])

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
