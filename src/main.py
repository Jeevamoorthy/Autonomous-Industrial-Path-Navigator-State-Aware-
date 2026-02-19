import cv2
import numpy as np
from utils import IPStream, trace_predictive_root, get_shortest_path, calculate_lookahead_action

def main():
    url = "http://192.0.0.4:8080/video"
    cam = IPStream(url)
    
    start_node = input("START AT: ")
    end_node = input("DESTINATION: ")
    route = get_shortest_path(start_node, end_node)
    if not route: return
    
    print(f"PATH: {' -> '.join(route)}")

    node_idx = 0
    state = "SEARCHING"
    last_cx = 160

    while True:
        frame = cam.read()
        if frame is None: continue
        
        # 1. Processing
        img_proc = cv2.resize(frame, (320, 240))
        roi = img_proc[100:, :]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([15, 60, 60]), np.array([35, 255, 255]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7,7), np.uint8))

        # 2. Vision
        path_pts, saw_junc, v_pos = trace_predictive_root(mask, last_cx)
        
        # 3. Decision Logic (Look-Ahead)
        curr_node = route[node_idx]
        # The node we are currently approaching
        next_node = route[node_idx+1] if node_idx+1 < len(route) else None
        # The node we want to go to AFTER the junction
        future_node = route[node_idx+2] if node_idx+2 < len(route) else None
        
        # Calculate the turn needed AT next_node to reach future_node
        action = calculate_lookahead_action(curr_node, next_node, future_node)

        # State transitions
        if state == "SEARCHING" and saw_junc and next_node:
            if v_pos < 0.5: state = "LOCKED"
        elif state == "LOCKED" and saw_junc and v_pos > 0.8:
            state = "TURNING"
        elif state == "TURNING" and (not saw_junc or v_pos > 0.95):
            node_idx += 1; state = "SEARCHING"

        # 4. UPSCALED HUD
        display = cv2.resize(img_proc, (640, 480))
        cv2.rectangle(display, (0, 0), (640, 110), (0, 0, 0), -1)
        
        status_color = (0, 255, 0) if state == "SEARCHING" else (0, 255, 255)
        cv2.putText(display, f"LOCATION: NODE {curr_node}", (20, 40), 0, 0.8, (255,255,255), 2)
        cv2.putText(display, f"STATUS: {state}", (350, 40), 0, 0.8, status_color, 2)
        
        if next_node:
            # Highlight the action to be taken at the upcoming junction
            msg = f"AT NODE {next_node}: {action}"
            cv2.putText(display, msg, (20, 85), 0, 1.0, (50, 255, 255), 2)
        else:
            cv2.putText(display, "ARRIVED AT DESTINATION", (20, 85), 0, 1.0, (0, 0, 255), 2)

        # Draw smooth path (Blue Polyline)
        if path_pts:
            last_cx = path_pts[0][0]
            pts_display = np.array([(p[0]*2, (p[1]+100)*2) for p in path_pts], np.int32)
            cv2.polylines(display, [pts_display.reshape((-1, 1, 2))], False, (255, 0, 0), 3)
            cv2.circle(display, tuple(pts_display[0]), 8, (0, 255, 0), -1)

        cv2.imshow("Robot Command Center", display)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()