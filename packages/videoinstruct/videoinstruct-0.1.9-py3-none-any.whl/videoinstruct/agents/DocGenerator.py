import os
import time
from typing import List, Optional, Dict, Any
import json
import litellm
from IPython.display import Markdown
import re

from videoinstruct.configs import DocGeneratorConfig
from videoinstruct.prompt_loader import DOC_GENERATOR_SYSTEM_PROMPT


class DocGenerator:
    """Generates documentation from video transcriptions using LLMs."""
    
    def __init__(
        self,
        config: Optional[DocGeneratorConfig] = None,
        transcription: Optional[str] = None,
        output_dir: str = "output"
    ) -> None:
        """Initialize the DocGenerator with configuration and optional transcription."""
        self.config = config or DocGeneratorConfig()
        self.model_provider = self.config.model_provider
        self.transcription = transcription
        self.conversation_history: List[Dict[str, str]] = []
        self.output_dir = output_dir
        
        if self.config.api_key:
            providers = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY"
            }
            if self.model_provider in providers:
                os.environ[providers[self.model_provider]] = self.config.api_key
        
        os.makedirs(output_dir, exist_ok=True)
    
    def set_transcription(self, transcription: str) -> None:
        """Set the video transcription and reset conversation history."""
        self.transcription = transcription
        self.conversation_history = []
    
    def generate_documentation(self) -> str:
        """Generate step-by-step documentation based on the video transcription."""
        if not self.transcription:
            raise ValueError("No transcription provided. Please set a transcription first.")
        
        initial_prompt = f"""
        Based on the following video transcription, create a step-by-step guide:
        
        TRANSCRIPTION:
        {self.transcription}
        
        Generate a detailed markdown guide that explains how to perform the task shown in the video.
        If you have any questions or need clarification about specific parts of the video, please ask.
        """
        
        self.conversation_history.append({"role": "user", "content": initial_prompt})
        response = self._get_llm_response(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def generate_documentation_with_description(self, initial_prompt: str) -> str:
        """Generate documentation based on both video transcription and detailed description."""
        self.conversation_history.append({"role": "user", "content": initial_prompt})
        response = self._get_llm_response(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def refine_documentation(self, feedback: str) -> str:
        """Refine the documentation based on feedback or additional information."""
        if not self.conversation_history:
            raise ValueError("No documentation has been generated yet.")
        
        self.conversation_history.append({"role": "user", "content": feedback})
        response = self._get_llm_response(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
        """Get a response from the LLM."""
        model_name = self.config.model
        if self.model_provider != "openai" and "/" not in model_name:
            model_name = f"{self.model_provider}/{model_name}"
        
        generate_config: Dict[str, Any] = {"drop_params": True}
        
        config_params = {
            "max_output_tokens": "max_tokens",
            "temperature": "temperature",
            "top_p": "top_p",
            "stream": "stream",
            "seed": "seed",
            "response_format": "response_format"
        }
        
        for param, config_key in config_params.items():
            if getattr(self.config, param, None) is not None:
                generate_config[config_key] = getattr(self.config, param)

        if self.config.system_instruction:
            system_message = {"role": "system", "content": self.config.system_instruction}
            messages = [system_message] + messages
        
        try:
            response = litellm.completion(
                model=model_name,
                messages=messages,
                **generate_config
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def save_documentation(self, filename: str = None) -> str:
        """Save the generated documentation to a markdown file."""
        if not self.conversation_history:
            raise ValueError("No documentation has been generated yet.")
        
        latest_doc = None
        for message in reversed(self.conversation_history):
            if message["role"] == "assistant":
                content = message["content"]
                try:
                    json_content = json.loads(content)
                    if isinstance(json_content, dict) and "content" in json_content:
                        if json_content.get("type") in ["documentation", "complete"]:
                            latest_doc = json_content["content"]
                            break
                except json.JSONDecodeError:
                    if not content.strip().endswith("?") and not content.startswith("VIDEO RESPONSE:"):
                        latest_doc = content
                        break
        
        if not latest_doc:
            raise ValueError("No documentation found in conversation history.")
        
        if not filename:
            title_match = re.search(r'^#\s+(.+)$', latest_doc, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
                filename = re.sub(r'[^\w\s-]', '', title).strip().lower()
                filename = re.sub(r'[-\s]+', '-', filename)
            else:
                filename = f"documentation-{int(time.time())}"
        
        if not filename.endswith('.md'):
            filename += '.md'
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(latest_doc)
        
        return file_path
    
    def display_documentation(self) -> Markdown:
        """Display the latest documentation as Markdown."""
        if not self.conversation_history:
            raise ValueError("No documentation has been generated yet.")
        
        latest_doc = None
        for message in reversed(self.conversation_history):
            if message["role"] == "assistant":
                content = message["content"]
                try:
                    json_content = json.loads(content)
                    if isinstance(json_content, dict) and "content" in json_content:
                        if json_content.get("type") in ["documentation", "complete"]:
                            latest_doc = json_content["content"]
                            break
                except json.JSONDecodeError:
                    if not content.strip().endswith("?") and not content.startswith("VIDEO RESPONSE:"):
                        latest_doc = content
                        break
        
        if not latest_doc:
            raise ValueError("No documentation found in conversation history.")
        
        return Markdown(latest_doc)
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from text."""
        questions = re.findall(r'(?:^|\n)\s*\d+\.\s*([^\n]+\?)', text)
        
        if not questions:
            questions = re.findall(r'([^.!?\n]+\?)', text)
        
        return questions