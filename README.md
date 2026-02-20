# Autonomous Industrial Path Navigator (State-Aware)

A high-speed, low-latency autonomous navigation stack for warehouse robots. This system moves beyond simple line-following by integrating **Topological Graph Mapping** with a **Predictive Path Crawler**.

## 🚀 Key Technical Features

*   **Predictive Path Crawler:** Instead of reactive thresholding, the algorithm "climbs" the line using granular sliding windows (8px height) to build a high-resolution 2D "spine" of the path.
*   **Topological Graph Logic:** The warehouse floor is represented as a mathematical graph (Adjacency List). The robot uses a BFS-based shortest-path solver to navigate from any Node A to Node B.
*   **Vector-Based Turn Prediction:** Uses cross-product vector math to determine if an upcoming junction requires a Left, Right, or Straight move based on the robot's entering trajectory.
*   **Zone-Based State Machine:** Implemented a 4-stage validation lock:
    1. **SEARCHING:** Scanning for path features.
    2. **LOCKED:** Advance warning of upcoming junction detected.
    3. **TURNING:** Physically entering the Action Zone.
    4. **ALIGNING:** Waiting for the camera to find a vertical straight line before updating the node location.
*   **Threaded IP Streamer:** Decouples frame grabbing from processing to ensure the robot always sees the *latest* frame, eliminating network latency issues common with IP cameras.


<img width="1625" height="906" alt="image" src="https://github.com/user-attachments/assets/9a20761d-10ac-4174-b49e-caf4043a937e" />
<img width="1627" height="914" alt="image" src="https://github.com/user-attachments/assets/615d48ac-37f0-40a6-b810-708be07db065" />
<img width="1625" height="913" alt="image" src="https://github.com/user-attachments/assets/c21e93da-6fac-41b6-83fe-1316a6de32b7" />


## 📂 Project Structure

```text
Robot_Navigation/
├── src/
│   ├── main.py          # Real-time Controller & State Machine
│   ├── utils.py         # Crawler Engine, Map Logic, & IP Streamer
│   └── config.py        # HSV Thresholds & ROI Settings
├── tests/
│   └── virtual_test.py  # GUI-based Logic Simulator
├── assets/              # Test videos and Map diagrams
└── logs/                # Mission recordings and telemetry CSVs


⚙️ Logic Flow
The robot follows a "Predict and Verify" loop:
Perception: Masking yellow paths and calculating line slope (Angle).
Prediction: Drawing a 30-point "Root" showing the line's curvature.
Decision: Comparing current vision data against the Topological Map.
Execution: HUD displays the next action (e.g., "TURN RIGHT TO 3") while the PID controller maintains center-line alignment.



Performance Targets
Processing Latency: < 4.0ms (Windows Prototype)
Throughput: 60+ FPS
Resolution: 320x240 (Optimized for Jetson Nano Deployment)
