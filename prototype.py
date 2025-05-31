import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Toplevel, Label, Entry, Button
from PIL import Image, ImageTk
import json
import sys
import geopandas as gpd
from shapely.geometry import Point
import subprocess
from geopy.geocoders import Nominatim

class MapApp:
    def __init__(self, root, map_file=None):
        self.root = root
        self.root.title("CBSE/ICSE Map Practice")
        self.last_score = None
        self.map_file = map_file
        self.exercise_mode = False 

        # Load geojson map
        self.gdf = gpd.read_file("Indian_Map.geojson")
        self.bounds = self.gdf.total_bounds  # [minx, miny, maxx, maxy]
        minx, miny, maxx, maxy = self.bounds
        self.map_width = 800
        self.map_height = 800
        self.bg = '#23272e'
        self.fg = '#e6e6e6'
        self.btn_bg = '#2d333b'
        self.btn_fg = '#e6e6e6'
        self.root.configure(bg=self.bg)

        # Layout: map on left, controls on right
        main_frame = tk.Frame(root, bg=self.bg)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add a canvas with scrollbars for the map
        canvas_frame = tk.Frame(main_frame, bg=self.bg)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=self.map_width, height=self.map_height, bg=self.bg, highlightbackground=self.bg)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Add scrollbars
        x_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        y_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set, scrollregion=(0, 0, self.map_width, self.map_height))
        # Enable mousewheel scrolling
        self.canvas.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        self.canvas.bind_all('<Shift-MouseWheel>', lambda e: self.canvas.xview_scroll(int(-1*(e.delta/120)), 'units'))

        # Draw polygons
        for _, row in self.gdf.iterrows():
            geom = row.geometry
            if geom.geom_type == 'Polygon':
                self._draw_polygon(geom)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    self._draw_polygon(poly)

        # Controls on the right
        control_frame = tk.Frame(main_frame, bg=self.bg)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(control_frame, text="Start Exercise", command=self.start_exercise, bg=self.btn_bg, fg=self.btn_fg, activebackground='#444', activeforeground=self.fg).pack(pady=10, padx=10, anchor='n')
        tk.Button(control_frame, text="Reset", command=self.reset_app, bg=self.btn_bg, fg=self.btn_fg, activebackground='#444', activeforeground=self.fg).pack(pady=10, padx=10, anchor='n')
        tk.Button(control_frame, text="Save Map", command=self.save_map, bg=self.btn_bg, fg=self.btn_fg, activebackground='#444', activeforeground=self.fg).pack(pady=10, padx=10, anchor='n')
        tk.Button(control_frame, text="Load Map", command=self.load_map, bg=self.btn_bg, fg=self.btn_fg, activebackground='#444', activeforeground=self.fg).pack(pady=10, padx=10, anchor='n')

        # Load points
        if map_file:
            with open(map_file, 'r') as f:
                data = json.load(f)
            self.points = data.get('points', [])
            self.last_score = data.get('last_score')
        else:
            self.points = []
        # Draw loaded points
        for pt in self.points:
            if pt.get("type") == "name":
                x, y = self.coord_to_canvas(pt["lon"], pt["lat"])
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="blue")
        # Bind click to canvas
        self.canvas.bind("<Button-1>", self.on_click)

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

    def _draw_polygon(self, poly):
        coords = [(self.coord_to_canvas(x, y)) for x, y in poly.exterior.coords]
        flat = [c for xy in coords for c in xy]
        self.canvas.create_polygon(flat, outline='#888', fill='#333', width=1)

    def coord_to_canvas(self, lon, lat):
        minx, miny, maxx, maxy = self.bounds
        x = (lon - minx) / (maxx - minx) * self.map_width
        y = self.map_height - (lat - miny) / (maxy - miny) * self.map_height
        return x, y

    def canvas_to_coord(self, x, y):
        minx, miny, maxx, maxy = self.bounds
        lon = minx + (x / self.map_width) * (maxx - minx)
        lat = miny + ((self.map_height - y) / self.map_height) * (maxy - miny)
        return lon, lat

    def on_click(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
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
                lon, lat = self.canvas_to_coord(cx, cy)
                if point_type == "name":
                    name = self.dark_simpledialog("Location Name", "Enter name of this location:")
                    if name:
                        self.points.append({"lon": lon, "lat": lat, "name": name, "type": "name"})
                        x, y = self.coord_to_canvas(lon, lat)
                        self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="blue")
                elif point_type == "find":
                    name = self.dark_simpledialog("Find Place", "Enter the name the user will have to find:")
                    if name:
                        self.points.append({"lon": lon, "lat": lat, "name": name, "type": "find"})
                        x, y = self.coord_to_canvas(lon, lat)
                        self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="green")
            tk.Button(type_dialog, text="OK", command=on_ok, bg='#2d333b', fg='#e6e6e6', activebackground='#444', activeforeground='#e6e6e6').pack(pady=10)
            type_dialog.transient(self.root)
            type_dialog.grab_set()
            self.root.wait_window(type_dialog)
        else:
            # In exercise mode, check if user clicked near any unanswered 'name' point
            for i, point in enumerate(self.points):
                if point.get("type") == "name" and not point.get("answered", False):
                    px, py = self.coord_to_canvas(point["lon"], point["lat"])
                    dx = cx - px
                    dy = cy - py
                    distance = (dx**2 + dy**2) ** 0.5
                    if distance <= 10:
                        self.canvas.create_oval(px-4, py-4, px+4, py+4, fill="red")
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
        # Use canvasx/canvasy for correct coordinates
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        point = self.current_find_point
        px, py = self.coord_to_canvas(point["lon"], point["lat"])
        dx = cx - px
        dy = cy - py
        distance = (dx**2 + dy**2) ** 0.5
        self.canvas.create_oval(px-4, py-4, px+4, py+4, outline="green", width=2)
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
        # Draw polygons
        for _, row in self.gdf.iterrows():
            geom = row.geometry
            if geom.geom_type == 'Polygon':
                self._draw_polygon(geom)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    self._draw_polygon(poly)
        for pt in self.points:
            if pt.get("type") == "name":
                pt["answered"] = False
                x, y = self.coord_to_canvas(pt["lon"], pt["lat"])
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="blue")
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
                "geojson": "Indian_Map.geojson",
                "points": self.points,
                "last_score": self.last_score
            }
            with open(file_path, 'w') as f:
                json.dump(data, f)
            self.dark_messagebox("Saved", f"Map saved to {file_path}", kind='info')
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
        # Redraw polygons
        for _, row in self.gdf.iterrows():
            geom = row.geometry
            if geom.geom_type == 'Polygon':
                self._draw_polygon(geom)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    self._draw_polygon(poly)
        if draw_points:
            for pt in self.points:
                if pt.get("type") == "name":
                    pt["answered"] = False
                    x, y = self.coord_to_canvas(pt["lon"], pt["lat"])
                    self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="blue")
        else:
            self.points = []

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    map_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = MapApp(root, map_file=map_file)
    root.mainloop()
