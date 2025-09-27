import socket
import uvicorn
import json
import os
import pigpio
import inspect
import time
import shutil
import tempfile
from contextlib import asynccontextmanager
import asyncio
from pyngrok import ngrok
from fastapi import FastAPI, APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv, set_key
import qrcode

# Import all hardware controllers and utility functions
from pi0ninja_v3.movement_recorder import ServoController, load_movements
from pi0disp.disp.st7789v import ST7789V
from pi0buzzer.driver import Buzzer
from vl53l0x_pigpio.driver import VL53L0X
from pi0ninja_v3.facial_expressions import AnimatedFaces
from pi0ninja_v3.robot_sound import RobotSoundPlayer
from pi0ninja_v3.ninja_agent import NinjaAgent

# --- Configuration and Setup ---
NINJA_ROBOT_V3_ROOT = "/home/rogerchang/NinjaRobotV3"
BUZZER_CONFIG_FILE = os.path.join(NINJA_ROBOT_V3_ROOT, "buzzer.json")
DOTENV_PATH = os.path.join(NINJA_ROBOT_V3_ROOT, ".env")

base_dir = os.path.dirname(os.path.abspath(__file__))
controllers = {}
api_router = APIRouter(prefix="/api")

# --- Pydantic Models for API requests ---
class SetApiKeyRequest(BaseModel):
    api_key: str

class AgentChatRequest(BaseModel):
    message: str

# --- Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("Initializing hardware controllers...")
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("Could not connect to pigpio daemon.")

    # Initialize controllers
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
    app.state.ninja_agent = None
    app.state.first_interaction = True

    # Load API Key and initialize Agent
    load_dotenv(dotenv_path=DOTENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            app.state.ninja_agent = NinjaAgent(api_key=api_key)
            print("Ninja AI Agent activated successfully from .env file.")
        except Exception as e:
            print(f"Error activating agent from .env file: {e}")
    else:
        print("GEMINI_API_KEY not found in .env file. AI Agent is not active.")

    print("All hardware and AI Agent initialized.")
    print("\nWaiting for application startup... (Press CTRL+C to quit)")

    async def network_setup_and_display():
        port = 8000
        hostname = socket.gethostname()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = "127.0.0.1"
        finally:
            s.close()

        print("--- NinjaRobot Web Server is starting! ---")
        print(f"Connect from a browser on the same network:\n  - By Hostname:  http://{hostname}.local:{port}\n  - By IP Address: http://{ip_address}:{port}")

        public_url = None
        for attempt in range(3):
            try:
                public_url = ngrok.connect(port, "http").public_url
                print(f"  - Secure Public URL (HTTPS): {public_url}")
                break
            except Exception as e:
                print(f"Could not start ngrok (attempt {attempt + 1}/3). Error: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    print("Failed to start ngrok after multiple attempts.")
        
        if public_url:
            try:
                print("Generating and displaying QR code on LCD...")
                qr_img = qrcode.make(public_url)
                qr_img = qr_img.convert('RGB')
                qr_img = qr_img.resize((controllers["display"].width, controllers["display"].height))
                controllers["display"].display(qr_img)
                print("QR code displayed. It will be cleared on first user interaction.")
            except Exception as e:
                print(f"Could not display QR code on LCD: {e}")
        else:
            # If ngrok fails, just go straight to idle
            await asyncio.to_thread(controllers["faces"].play_idle)

    asyncio.create_task(network_setup_and_display())
    
    yield

    # --- Shutdown ---
    print("Shutting down hardware controllers and ngrok...")
    controllers["faces"].stop() # Stop animation thread
    if controllers.get("servo"):
        controllers["servo"].cleanup()
    if controllers.get("display"):
        controllers["display"].close()
    if controllers.get("buzzer"):
        controllers["buzzer"].off()
    if controllers.get("distance_sensor"):
        controllers["distance_sensor"].close()
    pi.stop()
    ngrok.kill()

# --- Helper Functions ---

async def handle_first_interaction(request: Request):
    if request.app.state.first_interaction:
        request.app.state.first_interaction = False
        print("First interaction detected. Switching to idle face.")
        faces_controller = request.app.state.controllers.get("faces")
        if faces_controller:
            # The play_idle method is now thread-safe and manages its own thread
            await asyncio.to_thread(faces_controller.play_idle)

async def execute_robot_actions(request: Request, action_plan: dict):
    app_controllers = request.app.state.controllers
    face = action_plan.get("face")
    sound = action_plan.get("sound")
    movement = action_plan.get("movement")
    
    # Create a list of tasks to run concurrently
    action_tasks = []

    if face:
        faces_controller = app_controllers.get("faces")
        method_to_call = getattr(faces_controller, f"play_{face}", None)
        if method_to_call:
            async def play_face_and_return_to_idle():
                # This is a blocking call, so it runs in a thread
                await asyncio.to_thread(method_to_call, duration_s=3)
                # Once done, return to idle. Also a blocking call.
                await asyncio.to_thread(faces_controller.play_idle)
            action_tasks.append(asyncio.create_task(play_face_and_return_to_idle()))

    if sound:
        buzzer = app_controllers.get("buzzer")
        if buzzer:
            melody = RobotSoundPlayer.SOUNDS.get(sound)
            if melody:
                def play_sound_thread():
                    for note_name, duration in melody:
                        if note_name == 'pause':
                            time.sleep(duration)
                        else:
                            frequency = RobotSoundPlayer.NOTES.get(note_name)
                            if frequency:
                                buzzer.play_sound(frequency, duration)
                                time.sleep(0.01)  # Brief pause
                action_tasks.append(asyncio.to_thread(play_sound_thread))

    if movement:
        servo_controller = app_controllers.get("servo")
        all_movements = load_movements()
        sequence = all_movements.get(movement)
        if sequence and servo_controller:
            def run_movement():
                for step in sequence:
                    servo_controller.move_servos(step['moves'], step['speed'])
                    time.sleep(0.1)
            action_tasks.append(asyncio.to_thread(run_movement))

    if action_tasks:
        await asyncio.gather(*action_tasks)

# --- API Endpoints ---
@api_router.get("/agent/status")
async def agent_status(request: Request):
    return {"active": request.app.state.ninja_agent is not None}

@api_router.post("/agent/set_api_key")
async def set_api_key(payload: SetApiKeyRequest, request: Request):
    try:
        set_key(DOTENV_PATH, "GEMINI_API_KEY", payload.api_key)
        request.app.state.ninja_agent = NinjaAgent(api_key=payload.api_key)
        return {"status": "success", "message": "API key set and agent activated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set API key: {e}")

@api_router.post("/agent/chat")
async def agent_chat(payload: AgentChatRequest, request: Request):
    await handle_first_interaction(request)
    agent = request.app.state.ninja_agent
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not active.")
    result = await agent.process_command(payload.message)
    if "action_plan" in result and result["action_plan"]:
        asyncio.create_task(execute_robot_actions(request, result["action_plan"]))
    return {"response": result.get("response"), "log": result.get("log")}

@api_router.post("/agent/chat_voice")
async def agent_chat_voice(request: Request, audio_file: UploadFile = File(...)):
    await handle_first_interaction(request)
    agent = request.app.state.ninja_agent
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not active.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            shutil.copyfileobj(audio_file.file, tmp)
            tmp_path = tmp.name
        
        result = await agent.process_audio_command(tmp_path)
        
        if "action_plan" in result and result["action_plan"]:
            asyncio.create_task(execute_robot_actions(request, result["action_plan"]))
            
        return {"response": result.get("response"), "log": result.get("log")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {e}")
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        await audio_file.close()

# ... (rest of the endpoints remain the same)

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
        time.sleep(0.1)
    return {"status": f"Movement '{movement_name}' executed"}

@api_router.get("/display/expressions")
def get_facial_expressions(request: Request):
    faces_controller = request.app.state.controllers.get("faces")
    methods = inspect.getmembers(faces_controller, predicate=inspect.ismethod)
    return {"expressions": sorted([n.replace('play_', '') for n, _ in methods if n.startswith('play_')])}

@api_router.post("/display/expressions/{expression_name}")
def show_facial_expression(expression_name: str, request: Request):
    faces_controller = request.app.state.controllers.get("faces")
    method = getattr(faces_controller, f"play_{expression_name}", None)
    if not method:
        raise HTTPException(status_code=404, detail="Expression not found")
    method(duration_s=3)
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
        raise HTTPException(status_code=404, detail="Sound not found")
    for note, duration in melody:
        if note == 'pause':
            time.sleep(duration)
        else:
            frequency = RobotSoundPlayer.NOTES.get(note)
            if frequency:
                buzzer.play_sound(frequency, duration)
                time.sleep(0.01)
    return {"status": f"Sound for '{emotion_name}' played"}

@api_router.get("/sensor/distance")
def get_distance(request: Request):
    sensor = request.app.state.controllers.get("distance_sensor")
    return {"distance_mm": sensor.get_range()}

# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))
app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- WebSocket Endpoints ---
@app.websocket("/ws/distance")
async def websocket_distance_endpoint(websocket: WebSocket):
    await websocket.accept()
    sensor = websocket.app.state.controllers.get("distance_sensor")
    if not sensor:
        await websocket.close(code=1011, reason="Distance sensor not available")
        return
    try:
        while True:
            await websocket.send_json({"distance_mm": sensor.get_range()})
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        print("Client disconnected from distance websocket")

def main():
    port = 8000
    host = "0.0.0.0"
    uvicorn.run("pi0ninja_v3.web_server:app", host=host, port=port, reload=True, log_level="warning")

if __name__ == "__main__":
    main()