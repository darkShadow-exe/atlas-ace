import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Toplevel, Label, Entry, Button
from PIL import Image, ImageTk
import json
import sys

class MapApp:
    def __init__(self, root, map_file=None):
        self.root = root
        self.root.title("CBSE/ICSE Map Practice")
        self.last_score = None
        self.map_file = map_file

        # Load map image
        if map_file:
            with open(map_file, 'r') as f:
                data = json.load(f)
            img_path = data.get('image', 'image.png')
            self.points = data.get('points', [])
            self.last_score = data.get('last_score')
        else:
            img_path = "image.png"
            self.points = []
        self.map_img = Image.open(img_path)

        # Resize image to reasonable default size for display 
        max_size = 600
        original_width, original_height = self.map_img.size
        scale = min(max_size / original_width, max_size / original_height, 1)  # scale down only if larger than max_size
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        self.map_img = self.map_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(self.map_img)

        # Dark mode colors
        bg = '#23272e'
        fg = '#e6e6e6'
        btn_bg = '#2d333b'
        btn_fg = '#e6e6e6'
        self.root.configure(bg=bg)
        self.canvas = tk.Canvas(root, width=new_width, height=new_height, bg=bg, highlightbackground=bg)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

        self.exercise_mode = False
        self.current_index = 0

        # Draw loaded points 
        for pt in self.points:
            # Only show 'name' points (blue) at load
            if pt.get("type") == "name":
                self.canvas.create_oval(pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4, fill="blue")

        # Bind click to canvas
        self.canvas.bind("<Button-1>", self.on_click)

        # Control buttons
        btn_frame = tk.Frame(root, bg=bg)
        btn_frame.pack()
        tk.Button(btn_frame, text="Start Exercise", command=self.start_exercise, bg=btn_bg, fg=btn_fg, activebackground='#444', activeforeground=fg).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Reset", command=self.reset_app, bg=btn_bg, fg=btn_fg, activebackground='#444', activeforeground=fg).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Save Map", command=self.save_map, bg=btn_bg, fg=btn_fg, activebackground='#444', activeforeground=fg).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Load Map", command=self.load_map, bg=btn_bg, fg=btn_fg, activebackground='#444', activeforeground=fg).pack(side=tk.LEFT)

    def dark_simpledialog(self, title, prompt):
        dialog = Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg='#23272e')
        Label(dialog, text=prompt, bg='#23272e', fg='#e6e6e6').pack(padx=10, pady=10)
        entry = Entry(dialog, bg='#2d333b', fg='#e6e6e6', insertbackground='#e6e6e6')
        entry.pack(padx=10, pady=10)
        entry.focus_set()
        result = {'value': None}
        def on_ok():
            result['value'] = entry.get()
            dialog.destroy()
        Button(dialog, text="OK", command=on_ok, bg='#2d333b', fg='#e6e6e6', activebackground='#444', activeforeground='#e6e6e6').pack(pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        return result['value']

    def dark_messagebox(self, title, message, kind='info'):
        box = Toplevel(self.root)
        box.title(title)
        box.configure(bg='#23272e')
        Label(box, text=message, bg='#23272e', fg='#e6e6e6', wraplength=350).pack(padx=20, pady=20)
        def close():
            box.destroy()
        Button(box, text="OK", command=close, bg='#2d333b', fg='#e6e6e6', activebackground='#444', activeforeground='#e6e6e6').pack(pady=10)
        box.transient(self.root)
        box.grab_set()
        self.root.wait_window(box)

    def on_click(self, event):
        if not self.exercise_mode:
            # Select point type
            type_dialog = tk.Toplevel(self.root)
            type_dialog.title("Select Point Type")
            type_dialog.configure(bg='#23272e')
            tk.Label(type_dialog, text="Select point type:", bg='#23272e', fg='#e6e6e6').pack(padx=10, pady=5)
            point_type_var = tk.StringVar(value="name")
            rb1 = tk.Radiobutton(type_dialog, text="Name this point", variable=point_type_var, value="name", bg='#23272e', fg='#e6e6e6', selectcolor='#444')
            rb2 = tk.Radiobutton(type_dialog, text="Find this place", variable=point_type_var, value="find", bg='#23272e', fg='#e6e6e6', selectcolor='#444')
            rb1.pack(anchor='w', padx=20)
            rb2.pack(anchor='w', padx=20)
            def on_ok():
                type_dialog.destroy()
                point_type = point_type_var.get()
                if point_type == "name":
                    name = self.dark_simpledialog("Location Name", "Enter name of this location:")
                    if name:
                        self.points.append({"x": event.x, "y": event.y, "name": name, "type": "name"})
                        self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="blue")
                elif point_type == "find":
                    name = self.dark_simpledialog("Find Place", "Enter the name the user will have to find:")
                    if name:
                        self.points.append({"x": event.x, "y": event.y, "name": name, "type": "find"})
                        self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="green")
            tk.Button(type_dialog, text="OK", command=on_ok, bg='#2d333b', fg='#e6e6e6', activebackground='#444', activeforeground='#e6e6e6').pack(pady=10)
            type_dialog.transient(self.root)
            type_dialog.grab_set()
            self.root.wait_window(type_dialog)
        else:
            # In exercise mode, check if user clicked near any unanswered 'name' point
            for i, point in enumerate(self.points):
                if point.get("type") == "name" and not point.get("answered", False):
                    dx = event.x - point["x"]
                    dy = event.y - point["y"]
                    distance = (dx**2 + dy**2) ** 0.5
                    if distance <= 10:
                        self.canvas.create_oval(point["x"]-4, point["y"]-4, point["x"]+4, point["y"]+4, fill="red")
                        answer = self.dark_simpledialog("Guess the Place", f"What is the name of this location?")
                        if answer and answer.strip().lower() == point["name"].lower():
                            self.dark_messagebox("Correct", "Correct!", kind='info')
                            if not hasattr(self, 'score'):
                                self.score = 0
                            self.score += 1
                        else:
                            self.dark_messagebox("Incorrect", f"Incorrect.\nCorrect answer: {point['name']}", kind='error')
                        point["answered"] = True
                        break
            # After last name point, auto-start find points if any
            if self._at_end_of_name_points():
                self._start_find_points()
            else:
                self.check_exercise_end()
            
    def _at_end_of_name_points(self):
        # Returns True if all name points have been answered or there are no name points
        for pt in self.points:
            if pt.get("type") == "name" and not pt.get("answered", False):
                return False
        return True

    def _start_find_points(self):
        # Find the next 'find' point
        for idx, pt in enumerate(self.points):
            if pt.get("type") == "find":
                self.current_index = idx
                self.ask_find_point(pt)
                return
        # If no more find points, finish exercise
        self.current_index = len(self.points)
        self.check_exercise_end()

    def ask_find_point(self, point):
        self.dark_messagebox("Find Place", f"Click the location for: {point['name']}")
        self.canvas.unbind("<Button-1>")
        self.current_find_point = point
        self.canvas.bind("<Button-1>", self.check_find_point)

    def check_find_point(self, event):
        point = self.current_find_point
        dx = event.x - point["x"]
        dy = event.y - point["y"]
        distance = (dx**2 + dy**2) ** 0.5
        self.canvas.create_oval(point["x"]-4, point["y"]-4, point["x"]+4, point["y"]+4, outline="green", width=2)
        if distance <= 20:
            self.dark_messagebox("Correct", "Correct location!", kind='info')
            if not hasattr(self, 'score'):
                self.score = 0
            self.score += 1
        else:
            self.dark_messagebox("Incorrect", f"Incorrect location.\nCorrect spot was shown in green.", kind='error')
        # Move to next find point
        for i in range(self.current_index+1, len(self.points)):
            if self.points[i].get("type") == "find":
                self.current_index = i
                self.canvas.unbind("<Button-1>")
                self.ask_find_point(self.points[i])
                return
        # No more find points
        self.current_index = len(self.points)
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.on_click)
        self.check_exercise_end()

    def check_exercise_end(self):
        if self.current_index >= len(self.points):
            total = len(self.points)
            score = getattr(self, 'score', 0)
            self.dark_messagebox("Done", f"You've finished the exercise!\nScore: {score}/{total}", kind='info')
            self.last_score = score
            self.exercise_mode = False  
            if self.map_file:
                try:
                    with open(self.map_file, 'r') as f:
                        data = json.load(f)
                    data['last_score'] = score
                    with open(self.map_file, 'w') as f:
                        json.dump(data, f)
                except Exception:
                    pass
            else:
                self.save_map()

    def start_exercise(self):
        if not self.points:
            self.dark_messagebox("No Points", "Add points before starting exercise.", kind='warning')
            return
        self.exercise_mode = True
        self.current_index = 0
        self.score = 0
        # Redraw only 'name' points
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        for pt in self.points:
            if pt.get("type") == "name":
                pt["answered"] = False
                self.canvas.create_oval(pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4, fill="blue")
        self.dark_messagebox("Start", "Click each red dot and answer.", kind='info')
        if self._at_end_of_name_points():
            self._start_find_points()

    def save_map(self):
        if not self.points:
            self.dark_messagebox("No Points", "Add points before saving.", kind='warning')
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            data = {
                "image": "image.png",  
                "points": self.points,
                "last_score": self.last_score
            }
            with open(file_path, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Saved", f"Map saved to {file_path}")
            self.map_file = file_path

    def load_map(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.points = data.get('points', [])
            self.last_score = data.get('last_score')
            self.map_file = file_path
            self.reset_app(draw_points=True)

    def reset_app(self, draw_points=False):
        self.exercise_mode = False
        self.current_index = 0
        self.score = 0
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        if draw_points:
            for pt in self.points:
                if pt.get("type") == "name":
                    pt["answered"] = False
                    self.canvas.create_oval(pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4, fill="blue")
        else:
            self.points = []

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    map_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = MapApp(root, map_file=map_file)
    root.mainloop()
