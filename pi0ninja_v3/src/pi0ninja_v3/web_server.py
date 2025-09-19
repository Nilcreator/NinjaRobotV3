import socket
import uvicorn
import json
import os
import pigpio
import inspect
import time
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import all hardware controllers and utility functions
from pi0ninja_v3.movement_recorder import ServoController, load_movements
from pi0disp.disp.st7789v import ST7789V
from pi0buzzer.driver import Buzzer
from vl53l0x_pigpio.driver import VL53L0X
from pi0ninja_v3.facial_expressions import AnimatedFaces
from pi0ninja_v3.robot_sound import RobotSoundPlayer

# --- Configuration and Setup ---
NINJA_ROBOT_V3_ROOT = "/home/rogerchang/NinjaRobotV3"
BUZZER_CONFIG_FILE = os.path.join(NINJA_ROBOT_V3_ROOT, "buzzer.json")

# Determine the base directory of the web_server module
base_dir = os.path.dirname(os.path.abspath(__file__))

controllers = {}
api_router = APIRouter(prefix="/api")

# --- Hardware Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing hardware controllers...")
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("Could not connect to pigpio daemon.")

    controllers["servo"] = ServoController()
    controllers["display"] = ST7789V()
    controllers["distance_sensor"] = VL53L0X(pi)
    controllers["faces"] = AnimatedFaces(controllers["display"])

    try:
        with open(BUZZER_CONFIG_FILE, 'r') as f:
            buzzer_pin = json.load(f)['pin']
            controllers["buzzer"] = Buzzer(pi, buzzer_pin)
    except (FileNotFoundError, KeyError):
        print(f"Warning: {BUZZER_CONFIG_FILE} not found or invalid. Buzzer not initialized.")
        controllers["buzzer"] = None

    app.state.controllers = controllers
    yield

    print("Shutting down hardware controllers...")
    if controllers.get("servo"):
        controllers["servo"].cleanup()
    if controllers.get("display"):
        controllers["display"].close()
    if controllers.get("buzzer"):
        controllers["buzzer"].off()
    if controllers.get("distance_sensor"):
        controllers["distance_sensor"].close()
    pi.stop()

# --- API Endpoints ---
# (API endpoints remain the same)
@api_router.get("/servos/movements")
def get_servo_movements():
    return {"movements": list(load_movements().keys())}

@api_router.post("/servos/movements/{movement_name}/execute")
def execute_servo_movement(movement_name: str, request: Request):
    servo_controller = request.app.state.controllers.get("servo")
    all_movements = load_movements()
    if movement_name not in all_movements:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    sequence = all_movements[movement_name]
    for step in sequence:
        servo_controller.move_servos(step['moves'], step['speed'])
        time.sleep(0.1) # Small delay between steps
    return {"status": f"Movement '{movement_name}' executed"}

@api_router.get("/display/expressions")
def get_facial_expressions(request: Request):
    faces_controller = request.app.state.controllers.get("faces")
    methods = inspect.getmembers(faces_controller, predicate=inspect.ismethod)
    expression_names = [name.replace('play_', '') for name, _ in methods if name.startswith('play_')]
    return {"expressions": sorted(expression_names)}

@api_router.post("/display/expressions/{expression_name}")
def show_facial_expression(expression_name: str, request: Request):
    faces_controller = request.app.state.controllers.get("faces")
    method_to_call = getattr(faces_controller, f"play_{expression_name}", None)
    if not method_to_call:
        raise HTTPException(status_code=404, detail="Expression not found")
    method_to_call(duration_s=3)
    return {"status": f"Expression '{expression_name}' displayed"}

@api_router.get("/sound/emotions")
def get_emotion_sounds():
    return {"emotions": sorted(list(RobotSoundPlayer.SOUNDS.keys()))}

@api_router.post("/sound/emotions/{emotion_name}")
def play_emotion_sound(emotion_name: str, request: Request):
    buzzer = request.app.state.controllers.get("buzzer")
    if not buzzer:
        raise HTTPException(status_code=500, detail="Buzzer not initialized")
    
    melody = RobotSoundPlayer.SOUNDS.get(emotion_name)
    if not melody:
        raise HTTPException(status_code=404, detail="Emotion sound not found")

    for note_name, duration in melody:
        if note_name == 'pause':
            time.sleep(duration)
            continue
        frequency = RobotSoundPlayer.NOTES.get(note_name)
        if frequency:
            buzzer.play_sound(frequency, duration)
            time.sleep(0.01)
    return {"status": f"Sound for '{emotion_name}' played"}

@api_router.get("/sensor/distance")
def get_distance(request: Request):
    sensor = request.app.state.controllers.get("distance_sensor")
    distance = sensor.get_range()
    return {"distance_mm": distance}

# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/distance")
async def websocket_distance_endpoint(websocket: WebSocket):
    await websocket.accept()
    sensor = websocket.app.state.controllers.get("distance_sensor")
    if not sensor:
        await websocket.close(code=1011, reason="Distance sensor not available")
        return

    try:
        while True:
            distance = sensor.get_range()
            await websocket.send_json({"distance_mm": distance})
            await asyncio.sleep(0.2)  # ~5 Hz update rate
    except WebSocketDisconnect:
        print("Client disconnected from distance websocket")
    except Exception as e:
        print(f"Error in distance websocket: {e}")
        await websocket.close(code=1011, reason=f"An error occurred: {e}")

def main():
    """Main function to run the web server with a custom startup message."""
    port = 8000
    host = "0.0.0.0"

    # --- Get Hostname and IP Address ---
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
        print("Warning: Could not determine local IP address. Using localhost.")
    finally:
        s.close()

    # --- Print Custom Startup Message ---
    print("--- NinjaRobot Web Server is starting! ---")
    print("\nConnect to the robot from a browser on the same Wi-Fi network:")
    print(f"  - By Hostname:  http://{hostname}.local:{port}")
    print(f"  - By IP Address: http://{ip_address}:{port}")
    print("\nWaiting for application startup... (Press CTRL+C to quit)")

    # --- Run Uvicorn Server ---
    uvicorn.run(
        "pi0ninja_v3.web_server:app", 
        host=host, 
        port=port, 
        reload=True, 
        log_level="warning"
    )
