import numpy as np
import cv2
import threading
import time

# --- THE EXACT MAP FROM YOUR DRAWING ---
# Top Row: 1 --- 5 --- 4
# Bottom:  2 --- 3
# Connections: 5-3 is the vertical link. 1-2 is not connected.
NODE_COORDS = {
    "1": (0, 0),   "5": (10, 0),  "4": (20, 0),
    "2": (0, 10),  "3": (10, 10)
}

WAREHOUSE_GRAPH = {
    "1": ["5"],
    "5": ["1", "4", "3"],
    "4": ["5"],
    "3": ["5", "2"],
    "2": ["3"]
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

def calculate_lookahead_action(current_node, next_node, future_node):
    """Calculates the turn required AT the next_node to get to future_node."""
    if not next_node or not future_node: return "GO STRAIGHT"
    
    c = NODE_COORDS[str(current_node)]
    n = NODE_COORDS[str(next_node)]
    f = NODE_COORDS[str(future_node)]
    
    # Vector Entering Junction (c -> n)
    v1 = (n[0]-c[0], n[1]-c[1])
    # Vector Exiting Junction (n -> f)
    v2 = (f[0]-n[0], f[1]-n[1])
    
    # Cross product to determine Left/Right
    cross = v1[0]*v2[1] - v1[1]*v2[0]
    
    if cross == 0: return "STRAIGHT"
    # Flip logic based on camera mount: 
    # If it says Left but turns Right, swap these two strings.
    return "TURN LEFT" if cross > 0 else "TURN RIGHT"

def trace_predictive_root(mask, start_x):
    """Granular crawler for high-density path plotting."""
    path = []
    curr_x = start_x
    h, w = mask.shape
    curr_y = h - 5
    junc_found, junc_y = False, 0
    
    window_h = 8 
    for _ in range(25): # Plot 25 points ahead
        if curr_y < 10: break
        y1, y2 = max(0, curr_y - window_h), curr_y
        x1, x2 = max(0, curr_x-40), min(w, curr_x+40)
        win_roi = mask[y1:y2, x1:x2]
        
        if cv2.countNonZero(win_roi) > 80:
            M = cv2.moments(win_roi)
            cx = int(M["m10"]/M["m00"]) + x1
            path.append((cx, curr_y))
            curr_x = cx
        
        # Junction detection (Horizontal Density)
        if np.sum(mask[y1:y2, :]) > (w * 0.7 * 255):
            junc_found, junc_y = True, curr_y / h
        curr_y -= window_h
        
    return path, junc_found, junc_y

class IPStream:
    def __init__(self, url):
        self.stream = cv2.VideoCapture(url)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame = None
        self.stopped = False
        self.thread = threading.Thread(target=self.update, daemon=True).start()
    def update(self):
        while not self.stopped:
            ret, frame = self.stream.read()
            if ret: self.frame = frame
    def read(self): return self.frame
    def stop(self): self.stopped = True