import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
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

        self.canvas = tk.Canvas(root, width=new_width, height=new_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

        self.exercise_mode = False
        self.current_index = 0

        # Draw loaded points 
        for pt in self.points:
            self.canvas.create_oval(pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4, fill="blue")

        # Bind click to canvas
        self.canvas.bind("<Button-1>", self.on_click)

        # Control buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Start Exercise", command=self.start_exercise).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Reset", command=self.reset_app).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Save Map", command=self.save_map).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Load Map", command=self.load_map).pack(side=tk.LEFT)

    def on_click(self, event):
        if not self.exercise_mode:
            # Add mode
            name = simpledialog.askstring("Location Name", "Enter name of this location:")
            if name:
                self.points.append({"x": event.x, "y": event.y, "name": name})
                self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="blue")
        else:
            # Exercise mode
            if self.current_index >= len(self.points):
                return

            point = self.points[self.current_index]
            self.canvas.create_oval(point["x"]-4, point["y"]-4, point["x"]+4, point["y"]+4, fill="red")

            answer = simpledialog.askstring("Guess the Place", f"What is the name of this location?")
            if answer and answer.strip().lower() == point["name"].lower():
                messagebox.showinfo("Correct", "Correct!")
                if not hasattr(self, 'score'):
                    self.score = 0
                self.score += 1
            else:
                messagebox.showerror("Incorrect", f"Incorrect.\nCorrect answer: {point['name']}")

            self.current_index += 1
            if self.current_index >= len(self.points):
                total = len(self.points)
                score = getattr(self, 'score', 0)
                messagebox.showinfo("Done", f"You've finished the exercise!\nScore: {score}/{total}")
                self.last_score = score
                # Always save last_score to map file if possible
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
                    # If not loaded from file, prompt to save
                    self.save_map()

    def start_exercise(self):
        if not self.points:
            messagebox.showwarning("No Points", "Add points before starting exercise.")
            return
        self.exercise_mode = True
        self.current_index = 0
        self.score = 0
        messagebox.showinfo("Start", "Click each red dot and answer.")

    def save_map(self):
        if not self.points:
            messagebox.showwarning("No Points", "Add points before saving.")
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
                self.canvas.create_oval(pt["x"]-4, pt["y"]-4, pt["x"]+4, pt["y"]+4, fill="blue")
        else:
            self.points = []

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    map_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = MapApp(root, map_file=map_file)
    root.mainloop()
