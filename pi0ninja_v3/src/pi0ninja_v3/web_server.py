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
from pydantic import BaseModel
from dotenv import load_dotenv, set_key

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
    app.state.ninja_agent = None

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

# --- Helper function for non-blocking robot actions ---
async def execute_robot_actions(action_plan: dict, app_controllers: dict):
    face = action_plan.get("face")
    sound = action_plan.get("sound")
    movement = action_plan.get("movement")
    tasks = []
    if face:
        faces_controller = app_controllers.get("faces")
        method_to_call = getattr(faces_controller, f"play_{face}", None)
        if method_to_call:
            tasks.append(asyncio.to_thread(method_to_call, duration_s=3))
    if sound:
        buzzer = app_controllers.get("buzzer")
        if buzzer:
            melody = RobotSoundPlayer.SOUNDS.get(sound)
            if melody:
                def play_sound():
                    for note_name, duration in melody:
                        if note_name == 'pause':
                            time.sleep(duration)
                        else:
                            frequency = RobotSoundPlayer.NOTES.get(note_name)
                            if frequency:
                                buzzer.play_sound(frequency, duration)
                                time.sleep(0.01)
                tasks.append(asyncio.to_thread(play_sound))
    if tasks:
        await asyncio.gather(*tasks)
    if movement:
        servo_controller = app_controllers.get("servo")
        all_movements = load_movements()
        sequence = all_movements.get(movement)
        if sequence and servo_controller:
            def run_movement():
                for step in sequence:
                    servo_controller.move_servos(step['moves'], step['speed'])
                    time.sleep(0.1)
            await asyncio.to_thread(run_movement)

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
    agent = request.app.state.ninja_agent
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not active.")
    result = await agent.process_command(payload.message)
    if "action_plan" in result and result["action_plan"]:
        asyncio.create_task(execute_robot_actions(result["action_plan"], request.app.state.controllers))
    return {"response": result.get("response"), "log": result.get("log")}

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
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")),
            name="static")
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

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    agent = websocket.app.state.ninja_agent
    if not agent:
        await websocket.send_json({"type": "error", "data": "Agent not activated."})
        await websocket.close(code=1011)
        return

    audio_queue = asyncio.Queue()
    response_queue = asyncio.Queue()

    async def receive_audio():
        try:
            while True:
                await audio_queue.put(await websocket.receive_bytes())
        except WebSocketDisconnect:
            await audio_queue.put(None)

    async def run_agent():
        try:
            async for response in agent.stream_conversation(audio_queue):
                await response_queue.put(response)
        except Exception as e:
            await response_queue.put({"type": "error", "data": f"Agent error: {e}"})
        finally:
            await response_queue.put(None)

    async def send_responses():
        while True:
            response = await response_queue.get()
            if response is None:
                break
            if response.get("type") == "action":
                asyncio.create_task(execute_robot_actions(response["data"], websocket.app.state.controllers))
            await websocket.send_json(response)

    try:
        await asyncio.gather(receive_audio(), run_agent(), send_responses())
    except Exception as e:
        print(f"Error in voice websocket: {e}")
    finally:
        await websocket.close()

def main():
    port = 8000
    host = "0.0.0.0"
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
    print("\nWaiting for application startup... (Press CTRL+C to quit)")

    uvicorn.run("pi0ninja_v3.web_server:app", host=host, port=port, reload=True, log_level="warning")
