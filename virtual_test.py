import tkinter as tk
from tkinter import messagebox
import time
import threading

# --- 1. YOUR MAP DATA ---
# (Top line: 1-5-4 | Bottom line: 2-3 | Bridges: 1-2, 5-3)
NODE_POS = {
    "1": (150, 150), "5": (350, 150), "4": (550, 150),
    "2": (150, 400), "3": (350, 400)
}

WAREHOUSE_GRAPH = {
    "1": ["5", "2"],
    "5": ["1", "4", "3"],
    "4": ["5"],
    "2": ["1", "3"],
    "3": ["2", "5"]
}

# Real-world coords for Turn Calculation (Standard Cartesian)
LOGIC_COORDS = {
    "1": (0, 10), "5": (10, 10), "4": (20, 10),
    "2": (0, 0),  "3": (10, 0)
}

def get_shortest_path(start, end):
    queue = [[str(start)]]
    visited = set()
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == end: return path
        if node not in visited:
            for neighbor in WAREHOUSE_GRAPH.get(node, []):
                new_path = list(path); new_path.append(neighbor)
                queue.append(new_path)
            visited.add(node)
    return None

def calculate_action(p_node, c_node, n_node):
    if not p_node or not n_node: return "STRAIGHT"
    p, c, n = LOGIC_COORDS[p_node], LOGIC_COORDS[c_node], LOGIC_COORDS[n_node]
    v1 = (c[0]-p[0], c[1]-p[1])
    v2 = (n[0]-c[0], n[1]-c[1])
    cross = v1[0]*v2[1] - v1[1]*v2[0]
    if cross == 0: return "STRAIGHT"
    return "RIGHT TURN" if cross < 0 else "LEFT TURN"

# --- 2. GUI CLASS ---
class RobotSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial Robot Logic Tester")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        # Header
        self.header = tk.Label(root, text="ROBOT LOGIC TESTER", fg="#00FF00", bg="#121212", font=("Courier", 24, "bold"))
        self.header.pack(pady=10)

        # Canvas
        self.canvas = tk.Canvas(root, width=700, height=450, bg="#0a0a0a", highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(pady=10)

        # Controls
        self.ctrl_frame = tk.Frame(root, bg="#121212")
        self.ctrl_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        tk.Label(self.ctrl_frame, text="START:", fg="white", bg="#121212").pack(side="left")
        self.start_ent = tk.Entry(self.ctrl_frame, width=5)
        self.start_ent.insert(0, "4")
        self.start_ent.pack(side="left", padx=5)

        tk.Label(self.ctrl_frame, text="DESTINATION:", fg="white", bg="#121212").pack(side="left")
        self.dest_ent = tk.Entry(self.ctrl_frame, width=5)
        self.dest_ent.insert(0, "3")
        self.dest_ent.pack(side="left", padx=5)

        self.btn = tk.Button(self.ctrl_frame, text="SEND COMMAND", bg="#0078D7", fg="white", command=self.start_mission)
        self.btn.pack(side="left", padx=20)

        self.status_lbl = tk.Label(self.root, text="System Online. Waiting for coordinates...", fg="#00FF00", bg="#000", font=("Consolas", 10))
        self.status_lbl.pack(side="bottom", fill="x")

        self.robot = None
        self.draw_map()

    def draw_map(self):
        # Draw Connections
        for node, neighbors in WAREHOUSE_GRAPH.items():
            x1, y1 = NODE_POS[node]
            for n in neighbors:
                x2, y2 = NODE_POS[n]
                self.canvas.create_line(x1, y1, x2, y2, fill="#333", width=4)

        # Draw Nodes
        for node, (x, y) in NODE_POS.items():
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="#222", outline="#888", width=2)
            self.canvas.create_text(x, y, text=node, fill="white", font=("Arial", 12, "bold"))

    def start_mission(self):
        start = self.start_ent.get()
        dest = self.dest_ent.get()
        path = get_shortest_path(start, dest)
        
        if not path:
            messagebox.showerror("Error", "No path found!")
            return

        threading.Thread(target=self.run_logic, args=(path,), daemon=True).start()

    def run_logic(self, path):
        # Initial Robot Placement
        if self.robot: self.canvas.delete(self.robot)
        x, y = NODE_POS[path[0]]
        self.robot = self.canvas.create_oval(x-12, y-12, x+12, y+12, fill="red", outline="white", width=2)

        for i in range(len(path)):
            curr = path[i]
            prev = path[i-1] if i > 0 else None
            nxt = path[i+1] if i+1 < len(path) else None

            # 1. Update Position Visual
            rx, ry = NODE_POS[curr]
            self.canvas.coords(self.robot, rx-12, ry-12, rx+12, ry+12)
            
            # 2. Calculate Decision
            action = calculate_action(prev, curr, nxt)
            
            # 3. Display Logic
            status = f"AT NODE {curr}"
            if nxt:
                status += f" | DECISION: {action} TO NODE {nxt}"
                self.status_lbl.config(text=f">>> {status}", fg="yellow")
            else:
                self.status_lbl.config(text=f">>> MISSION COMPLETE: ARRIVED AT {curr}", fg="#00FF00")
            
            print(status)
            time.sleep(1.5) # Wait at node to show decision

root = tk.Tk()
sim = RobotSimulator(root)
root.mainloop()