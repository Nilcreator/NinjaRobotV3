import os
import json
import time
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, Tool
from pi0ninja_v3.facial_expressions import AnimatedFaces
from pi0ninja_v3.robot_sound import RobotSoundPlayer
from googlesearch import search

class NinjaAgent:
    """
    An AI agent for the NinjaRobot that handles text-based conversations.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")

        genai.configure(api_key=api_key)
        
        self.robot_capabilities = self._load_robot_capabilities()
        self.system_prompt = self._create_system_prompt()
        
        self.search_tool = Tool(
            function_declarations=[
                {
                    "name": "web_search",
                    "description": "Search the internet for information. Use for questions about weather, news, facts, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string", "description": "The search query."}},
                        "required": ["query"]
                    }
                }
            ]
        )

        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config=GenerationConfig(temperature=0.7),
            tools=[self.search_tool],
            system_instruction=self.system_prompt
        )

    def _load_robot_capabilities(self) -> dict:
        movements, faces, sounds = [], [], []
        try:
            movement_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'servo_movement.json'))
            with open(movement_file_path, 'r') as f:
                movements = list(json.load(f).keys())
        except FileNotFoundError:
            print("Warning: servo_movement.json not found.")
        faces = [func.replace('play_', '') for func in dir(AnimatedFaces) if func.startswith('play_')]
        sounds = list(RobotSoundPlayer.SOUNDS.keys())
        return {"movements": movements, "faces": faces, "sounds": sounds}

    def _create_system_prompt(self) -> str:
        return f"""You are Ninja, a small robot. You will receive user commands as text or audio. Respond naturally and conversationally. You can perform physical actions or search the web.

1.  **Physical Actions**: If the user asks you to do something, respond with a **valid JSON object** to control your body. Your available actions are:
    - movements: {self.robot_capabilities['movements']}
    - faces: {self.robot_capabilities['faces']}
    - sounds: {self.robot_capabilities['sounds']}
    The JSON format is: {{"movement": "...", "face": "...", "sound": "...", "response": "..."}}
    **IMPORTANT**: The JSON you output **MUST** be perfectly valid. Always use double quotes for keys and string values.

2.  **Web Search**: For questions you can't answer, use the `web_search` tool.

Keep your spoken responses short and friendly. Always respond in the same language as the user.
"""

    def web_search(self, query: str) -> list[str]:
        """Performs a web search and returns the results."""
        try:
            return list(search(query, num_results=5))
        except Exception as e:
            print(f"Error during web search: {e}")
            return ["Search failed."]

    async def process_command(self, user_input: str) -> dict:
        """ Processes a text-based user command. """
        log_messages = []
        try:
            chat = self.model.start_chat()
            response = await chat.send_message_async(user_input)
            function_call = response.candidates[0].content.parts[0].function_call

            if function_call.name:
                if function_call.name == "web_search":
                    query = function_call.args['query']
                    log_messages.append(f"AI wants to search for: {query}")
                    search_results = self.web_search(query=query)
                    log_messages.append("Web search executed.")
                    response = await chat.send_message_async(
                        content={"parts": [{"function_response": {"name": "web_search", "response": {"results": search_results}}}]}
                    )
                else:
                    raise ValueError(f"Unknown function call: {function_call.name}")

            cleaned_response_text = response.candidates[0].content.parts[0].text.strip()
            json_start = cleaned_response_text.find('{')
            json_end = cleaned_response_text.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                action_plan = {"movement": None, "face": "speaking", "sound": "speaking", "response": cleaned_response_text}
            else:
                json_str = cleaned_response_text[json_start:json_end]
                print(f"""--- DEBUG: Attempting to parse JSON: ---
{json_str}
-----------------------------------------""")
                action_plan = json.loads(json_str)

            log_messages.append(f"AI Action Plan: {action_plan}")
            final_log = '\n'.join(log_messages)
            print(final_log)

            return {"action_plan": action_plan, "response": action_plan.get("response"), "log": final_log}

        except Exception as e:
            error_message = f"Error processing command: {e}"
            print(error_message)
            return {"action_plan": {}, "response": "I'm sorry, something went wrong.", "log": error_message}

    async def process_audio_command(self, audio_file_path: str) -> dict:
        """Processes a voice command from an audio file."""
        log_messages = [f"Processing audio file: {audio_file_path}"]
        audio_file = None
        try:
            # Upload the audio file to the Gemini API
            log_messages.append("Uploading audio file...")
            audio_file = genai.upload_file(path=audio_file_path, mime_type="audio/webm")
            log_messages.append(f"Audio file uploaded: {audio_file.name}. Waiting for it to become active...")

            # Wait for the file to be processed
            timeout_seconds = 60
            start_time = time.time()
            while audio_file.state.name == "PROCESSING":
                if time.time() - start_time > timeout_seconds:
                    raise TimeoutError("File processing timed out.")
                time.sleep(2)
                audio_file = genai.get_file(name=audio_file.name)

            if audio_file.state.name != "ACTIVE":
                raise ValueError(f"Uploaded file is not active. Current state: {audio_file.state.name}")

            log_messages.append("Audio file is active. Sending to model.")

            # Send the audio file and a prompt to the model
            prompt = "Transcribe this audio. Based on the transcription, decide whether to perform a physical action or a web search, and then respond."
            response = await self.model.generate_content_async([prompt, audio_file])

            # The response will contain the transcribed text, which the model
            # should have processed as a command.
            # We can then extract the action plan and response as in process_command.
            
            cleaned_response_text = response.candidates[0].content.parts[0].text.strip()
            json_start = cleaned_response_text.find('{')
            json_end = cleaned_response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                # No JSON action plan found, treat the whole response as text
                action_plan = {"movement": None, "face": "speaking", "sound": "speaking", "response": cleaned_response_text}
            else:
                # JSON action plan found
                json_str = cleaned_response_text[json_start:json_end]
                print(f"""--- DEBUG: Attempting to parse JSON from audio command: ---
{json_str}
-------------------------------------------------""")
                action_plan = json.loads(json_str)

            log_messages.append(f"AI Action Plan from Audio: {action_plan}")
            final_log = '\n'.join(log_messages)
            print(final_log)

            return {"action_plan": action_plan, "response": action_plan.get("response"), "log": final_log}

        except Exception as e:
            error_message = f"Error processing audio command: {e}"
            print(error_message)
            return {"action_plan": {}, "response": "I'm sorry, I had trouble understanding the audio.", "log": error_message}
        finally:
            # It's good practice to clean up the uploaded file
            if audio_file and hasattr(audio_file, 'name'):
                try:
                    genai.delete_file(audio_file.name)
                    log_messages.append(f"Cleaned up uploaded file: {audio_file.name}")
                    print(f"Cleaned up uploaded file: {audio_file.name}")
                except Exception as delete_e:
                    print(f"Error deleting uploaded file: {delete_e}")
