import os
import json
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, Tool
from pi0ninja_v3.facial_expressions import AnimatedFaces
from pi0ninja_v3.robot_sound import RobotSoundPlayer
from googlesearch import search

class NinjaAgent:
    """
    An AI agent for the NinjaRobot that handles both text and streaming voice conversations.
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
        # (This method remains the same)
        movements, faces, sounds = [], [], []
        try:
            movement_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../', 'servo_movement.json'))
            with open(movement_file_path, 'r') as f:
                movements = list(json.load(f).keys())
        except FileNotFoundError:
            print("Warning: servo_movement.json not found.")
        faces = [func.replace('play_', '') for func in dir(AnimatedFaces) if func.startswith('play_')]
        sounds = list(RobotSoundPlayer.SOUNDS.keys())
        return {"movements": movements, "faces": faces, "sounds": sounds}

    def _create_system_prompt(self) -> str:
        # (Prompt is simplified for streaming context)
        return f"""You are Ninja, a small robot. You will receive a real-time audio transcription of a user speaking to you. Respond naturally and conversationally. You can perform physical actions or search the web.

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
        # This is a synchronous call, which might block the event loop.
        # For a production system, consider running this in a separate thread.
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
                print(f"--- DEBUG: Attempting to parse JSON: ---\n{json_str}\n-----------------------------------------")
                action_plan = json.loads(json_str)

            log_messages.append(f"AI Action Plan: {action_plan}")
            final_log = '\n'.join(log_messages)
            print(final_log)

            return {"action_plan": action_plan, "response": action_plan.get("response"), "log": final_log}

        except Exception as e:
            error_message = f"Error processing command: {e}"
            print(error_message)
            return {"action_plan": {}, "response": "I'm sorry, something went wrong.", "log": error_message}

    async def process_audio_input(self, audio_bytes: bytes) -> dict:
        """Processes a complete audio recording."""
        log_messages = ["Received audio file, sending to Gemini for processing..."]
        try:
            # The model can take audio and text in the same prompt
            response = await self.model.generate_content_async([
                "Transcribe the user's command from this audio and execute it.", 
                {"mime_type": "audio/webm", "data": audio_bytes}
            ])

            # The rest of this logic is similar to process_command
            function_call = response.candidates[0].content.parts[0].function_call

            if function_call.name:
                if function_call.name == "web_search":
                    query = function_call.args['query']
                    log_messages.append(f"AI wants to search for: {query}")
                    search_results = self.web_search(query=query)
                    log_messages.append("Web search executed.")
                    response = await self.model.generate_content_async(
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
                action_plan = json.loads(json_str)

            log_messages.append(f"AI Action Plan: {action_plan}")
            final_log = '\n'.join(log_messages)
            print(final_log)

            return {"action_plan": action_plan, "response": action_plan.get("response"), "log": final_log}

        except Exception as e:
            error_message = f"Error processing audio: {e}"
            print(error_message)
            return {"action_plan": {}, "response": "I had trouble understanding that.", "log": error_message}
