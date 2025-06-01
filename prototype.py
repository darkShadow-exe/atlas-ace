import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Toplevel, Label, Entry, Button
from PIL import Image, ImageTk
import json
import sys
import geopandas as gpd
from shapely.geometry import Point
import subprocess
from geopy.geocoders import Nominatim
import requests

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
        tk.Button(control_frame, text="AI Exercise (Llama)", command=self.open_llama_custom_dialog, bg=self.btn_bg, fg=self.btn_fg, activebackground='#444', activeforeground=self.fg).pack(pady=10, padx=10, anchor='n')

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

    def ask_llama_questions(self, custom_instructions):
        """
        Calls llama3 via Ollama to generate map questions, geocodes them, and loads them as points.
        custom_instructions: dict with keys num_questions, type_ratio, filter_topics, include_history
        """
        # Show loading screen
        loading = Toplevel(self.root)
        loading.title("Loading")
        loading.configure(bg=self.bg)
        Label(loading, text="Generating questions with Llama...\nThis may take a moment.", bg=self.bg, fg=self.fg).pack(padx=30, pady=30)
        loading.transient(self.root)
        loading.grab_set()
        self.root.update()

        prompt = f"""
You are an educational AI assistant creating a map-based learning dataset for CBSE Class 10. Use the syllabus below to generate question-answer pairs.

Follow these custom instructions:
- Total questions: {custom_instructions['num_questions']}
- Ratio of 'find' (map click) to 'name' (user types name): {custom_instructions['type_ratio'][0]} : {custom_instructions['type_ratio'][1]}
- Topics to include: {'All' if not custom_instructions['filter_topics'] else ', '.join(custom_instructions['filter_topics'])}
- Include history-related questions: {'Yes' if custom_instructions['include_history'] else 'No'}

---

SYLLABUS  
{"History – Chapter 2: Nationalism in India (1918–1930)" if custom_instructions['include_history'] else ""}
{"- Indian National Congress Sessions: Calcutta (Sept 1920), Nagpur (Dec 1920), Madras (1927)" if custom_instructions['include_history'] else ""}
{"- Centres of the Indian National Movement: Champaran (Bihar), Kheda (Gujarat), Ahmedabad (Gujarat), Amritsar (Punjab), Dandi (Gujarat)" if custom_instructions['include_history'] else ""}

Geography – Chapter 3: Water Resources  
- Dams: Salal, Bhakra Nangal, Tehri, Rana Pratap Sagar, Sardar Sarovar, Hirakud, Nagarjuna Sagar, Tungabhadra

Geography – Chapter 5: Minerals and Energy Resources  
- Iron Ore Mines: Mayurbhanj, Durg, Bailadila, Bellary, Kudremukh  
- Coal Mines: Raniganj, Bokaro, Talcher, Neyveli  
- Oil Fields: Digboi, Naharkatia, Mumbai High, Bassien, Kalol, Ankleshwar  
- Power Plants:  
  - Thermal: Namrup, Singrauli, Ramagundam  
  - Nuclear: Narora, Kakrapara, Tarapur, Kalpakkam

Geography – Chapter 6: Manufacturing Industries  
- Cotton Textile: Mumbai, Indore, Surat, Kanpur, Coimbatore  
- Iron & Steel: Durgapur, Bokaro, Jamshedpur, Bhilai, Vijayanagar, Salem  
- Software Tech Parks: Noida, Gandhinagar, Mumbai, Pune, Hyderabad, Bengaluru, Chennai, Thiruvananthapuram

Geography – Chapter 7: Lifelines of National Economy  
- Major Sea Ports: Kandla, Mumbai, Marmagao, New Mangalore, Kochi, Tuticorin, Chennai, Vishakhapatnam, Paradip, Haldia  
- International Airports: Amritsar, Delhi, Mumbai, Chennai, Kolkata, Hyderabad

---

OUTPUT FORMAT  
Return a JSON array with each object in this format:

{{
  "question": "Where is the Bhakra Nangal Dam located?",
  "answer": "Bhakra Nangal",
  "place": "Bhakra Nangal, India",
  "category": "Geography",
  "chapter": "Water Resources",
  "topic": "Dams",
  "type": "name" // or "find"
}}

Point Type Explanation:  
- "name" → User sees a location on the map and must type the name.  
- "find" → User sees the name and must click the location on the map.

Maintain the specified ratio between 'find' and 'name' question types.  
Use only city/town + state or country in the place field for compatibility with Nominatim.  
If filter_topics is set, only include questions from those topics.  
Return only the JSON array.
"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": True
            }
        )
        full_output = ""
        if response.ok:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        full_output += data["response"]
        else:
            loading.destroy()
            self.dark_messagebox("Error", f"Llama request failed: {response.status_code}", kind='error')
            return
        try:
            json_start = full_output.find("[")
            json_end = full_output.rfind("]") + 1
            parsed_data = json.loads(full_output[json_start:json_end])
            # Show the raw JSON output in a debug window
            debug_win = Toplevel(self.root)
            debug_win.title("Llama JSON Output (Debug)")
            debug_win.configure(bg=self.bg)
            text = tk.Text(debug_win, bg=self.bg, fg=self.fg, insertbackground=self.fg, wrap='none', width=120, height=30)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert('1.0', json.dumps(parsed_data, indent=2))
            text.config(state='disabled')
        except Exception as e:
            loading.destroy()
            self.dark_messagebox("Error", f"Error parsing JSON: {str(e)}", kind='error')
            return
        geolocator = Nominatim(user_agent="atlas-ace-geocoder")
        points = []
        for obj in parsed_data:
            place = obj.get("place")
            lon, lat = None, None
            if place:
                try:
                    location = geolocator.geocode(place)
                    if location:
                        lon, lat = location.longitude, location.latitude
                except Exception:
                    pass
            if lon is not None and lat is not None:
                points.append({
                    "lon": lon,
                    "lat": lat,
                    "name": obj.get("answer"),
                    "type": obj.get("type", "name"),
                    "question": obj.get("question"),
                    "category": obj.get("category"),
                    "chapter": obj.get("chapter"),
                    "topic": obj.get("topic"),
                    "place": place
                })
        loading.destroy()
        # Show the processed points in a debug window
        debug_points = Toplevel(self.root)
        debug_points.title("Processed Points (Debug)")
        debug_points.configure(bg=self.bg)
        text2 = tk.Text(debug_points, bg=self.bg, fg=self.fg, insertbackground=self.fg, wrap='none', width=120, height=30)
        text2.pack(fill=tk.BOTH, expand=True)
        text2.insert('1.0', json.dumps(points, indent=2))
        text2.config(state='disabled')
        if not points:
            self.dark_messagebox("No Points", "No valid points generated.", kind='warning')
            return
        self.points = points
        self.exercise_mode = True
        self.current_index = 0
        self.score = 0
        self.canvas.delete("all")
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
        self.dark_messagebox("Start", "Click each blue dot and answer.", kind='info')
        if self._at_end_of_name_points():
            self._start_find_points()

    def open_llama_custom_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("AI Exercise Custom Instructions")
        dialog.configure(bg=self.bg)
        # Number of questions
        Label(dialog, text="Number of questions:", bg=self.bg, fg=self.fg).pack(padx=10, pady=2)
        num_q = Entry(dialog, bg=self.btn_bg, fg=self.fg, insertbackground=self.fg)
        num_q.insert(0, "10")
        num_q.pack(padx=10, pady=2)
        # Ratio
        Label(dialog, text="Ratio of find:name (e.g. 0.5:0.5):", bg=self.bg, fg=self.fg).pack(padx=10, pady=2)
        ratio = Entry(dialog, bg=self.btn_bg, fg=self.fg, insertbackground=self.fg)
        ratio.insert(0, "0.5:0.5")
        ratio.pack(padx=10, pady=2)
        # Topics
        Label(dialog, text="Filter topics (comma separated, blank for all):", bg=self.bg, fg=self.fg).pack(padx=10, pady=2)
        topics = Entry(dialog, bg=self.btn_bg, fg=self.fg, insertbackground=self.fg)
        topics.pack(padx=10, pady=2)
        # History
        include_hist = tk.IntVar(value=1)
        tk.Checkbutton(dialog, text="Include history questions", variable=include_hist, bg=self.bg, fg=self.fg, selectcolor='#444').pack(padx=10, pady=2)
        def on_ok():
            try:
                n = int(num_q.get())
            except Exception:
                n = 10
            try:
                r = [float(x) for x in ratio.get().split(":")]
                if len(r) != 2 or abs(sum(r)-1) > 0.01:
                    r = [0.5, 0.5]
            except Exception:
                r = [0.5, 0.5]
            t = [x.strip() for x in topics.get().split(",") if x.strip()]
            custom = {
                "num_questions": n,
                "type_ratio": r,
                "filter_topics": t,
                "include_history": bool(include_hist.get())
            }
            dialog.destroy()
            self.ask_llama_questions(custom)
        Button(dialog, text="OK", command=on_ok, bg=self.btn_bg, fg=self.fg, activebackground='#444', activeforeground=self.fg).pack(pady=10)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    map_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = MapApp(root, map_file=map_file)
    root.mainloop()
