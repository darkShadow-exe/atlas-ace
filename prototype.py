import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk

class MapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CBSE/ICSE Map Practice")

        # Load map image
        self.map_img = Image.open("image.png")
        self.tk_img = ImageTk.PhotoImage(self.map_img)

        self.canvas = tk.Canvas(root, width=self.tk_img.width(), height=self.tk_img.height())
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
