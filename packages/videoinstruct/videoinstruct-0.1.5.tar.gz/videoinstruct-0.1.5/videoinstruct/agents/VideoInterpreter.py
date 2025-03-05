from google import genai
from google.genai import types
import time
import os
from typing import Optional, List, Dict, Any
from IPython.display import Markdown

from videoinstruct.configs import VideoInterpreterConfig


class VideoInterpreter:
    """Interprets videos using Google's Gemini API."""
    
    def __init__(
        self,
        config: Optional[VideoInterpreterConfig] = None,
        video_path: Optional[str] = None
    ) -> None:
        """Initialize the VideoInterpreter with config and optional video."""
        self.config = config or VideoInterpreterConfig()
        
        self.api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided in config or set as GEMINI_API_KEY environment variable")
        
        self.client = genai.Client(api_key=self.api_key)
        self.video_file = None
        self.conversation_history: List[str] = []
        
        if video_path:
            self.load_video(video_path)
    
    def load_video(self, video_path: str) -> None:
        """Load a video file for interpretation."""
        self.video_file = self.client.files.upload(file=video_path)
        
        while self.video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            self.video_file = self.client.files.get(name=self.video_file.name)
        
        if self.video_file.state.name == "FAILED":
            raise ValueError(f"Video processing failed: {self.video_file.state.name}")
        
        print('Video loaded successfully')
        self.conversation_history = []
    
    def respond(self, question: str) -> str:
        """Respond to a question about the loaded video."""
        if not self.video_file:
            raise ValueError("No video loaded. Please load a video first using load_video().")
        
        self.conversation_history.append(f"user: {question}")
        
        contents = [self.video_file]
        if self.conversation_history:
            contents.append(", ".join(self.conversation_history))
        
        generate_config: Dict[str, Any] = {}
        
        config_params = {
            "system_instruction": "system_instruction",
            "max_output_tokens": "max_output_tokens",
            "top_k": "top_k",
            "top_p": "top_p",
            "temperature": "temperature",
            "response_mime_type": "response_mime_type",
            "stop_sequences": "stop_sequences",
            "seed": "seed"
        }
        
        for param, config_key in config_params.items():
            if getattr(self.config, param, None) is not None:
                generate_config[config_key] = getattr(self.config, param)
        
        response = self.client.models.generate_content(
            contents=contents,
            model=self.config.model,
            config=types.GenerateContentConfig(**generate_config),
        )
        
        self.conversation_history.append(f"assistant: {response.text}")
        
        return response.text
    
    def remove_memory(self) -> None:
        """Reset the conversation history while keeping the video loaded."""
        self.conversation_history = []
    
    def delete_video(self) -> None:
        """Delete the loaded video and reset the conversation history."""
        if not self.video_file:
            return
        
        try:
            self.client.files.delete(name=self.video_file.name)
            self.video_file = None
            self.conversation_history = []
        except genai.errors.ClientError as e:
            raise ValueError(f"Error deleting video: {e.message}")
    
    def display_response(self, response_text: str) -> Markdown:
        """Display the response as Markdown."""
        return Markdown(response_text)