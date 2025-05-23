import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

class MapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CBSE/ICSE Map Practice")

        # Load map image
        self.map_img = Image.open("image.png")

        # Resize image to reasonable default size for display (max width or height 600)
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

        self.points = [] 
        self.exercise_mode = False
        self.current_index = 0

        # Bind click to canvas
        self.canvas.bind("<Button-1>", self.on_click)

        # Control buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Start Exercise", command=self.start_exercise).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Reset", command=self.reset_app).pack(side=tk.LEFT)

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
            else:
                messagebox.showerror("Incorrect", f"Incorrect.\nCorrect answer: {point['name']}")

            self.current_index += 1
            if self.current_index >= len(self.points):
                messagebox.showinfo("Done", "You've finished the exercise!")

    def start_exercise(self):
        if not self.points:
            messagebox.showwarning("No Points", "Add points before starting exercise.")
            return
        self.exercise_mode = True
        self.current_index = 0
        messagebox.showinfo("Start", "Click each red dot and answer.")

    def reset_app(self):
        self.points = []
        self.exercise_mode = False
        self.current_index = 0
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MapApp(root)
    root.mainloop()
