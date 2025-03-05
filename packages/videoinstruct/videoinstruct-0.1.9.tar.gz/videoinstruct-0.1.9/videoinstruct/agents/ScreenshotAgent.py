import os
import re
import sys
import json
import time
from typing import Optional, Dict, Any
from PIL import Image
from google import generativeai as genai

# Add the parent directory to the Python path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from videoinstruct.configs import ScreenshotAgentConfig, VideoInterpreterConfig
from videoinstruct.agents.VideoInterpreter import VideoInterpreter
from videoinstruct.tools.video_screenshot import VideoScreenshotTool


class ScreenshotAgent:
    """Agent for extracting and integrating screenshots into Markdown documentation."""
    
    def __init__(
        self,
        config: Optional[ScreenshotAgentConfig] = None,
        video_interpreter: Optional[VideoInterpreter] = None,
        video_path: Optional[str] = None,
        output_dir: str = "output"
    ):
        """Initialize the ScreenshotAgent with configuration and resources."""
        self.config = config or ScreenshotAgentConfig()
        self.video_interpreter = video_interpreter
        self.video_path = video_path
        self.output_dir = output_dir
        
        # Cache file path for storing screenshot mappings
        self.cache_file = os.path.join(output_dir, "screenshot_cache.json")
        # Screenshots cache: {normalized_name: screenshot_path}
        self.screenshot_cache = self._load_screenshot_cache()
        
        # List to track unavailable screenshots
        self.unavailable_screenshots = []
        
        # Get API key from config or environment variable
        self.api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided in config or set as GEMINI_API_KEY environment variable")
        
        # Initialize Gemini client
        genai.api_key = self.api_key
        
        # Configure the model with system instruction
        generation_config = {
            "temperature": self.config.temperature,
        }
        
        if self.config.max_output_tokens:
            generation_config["max_output_tokens"] = self.config.max_output_tokens
        if self.config.top_p:
            generation_config["top_p"] = self.config.top_p
        if self.config.top_k:
            generation_config["top_k"] = self.config.top_k
        if self.config.seed:
            generation_config["seed"] = self.config.seed
        
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config=generation_config,
            system_instruction=self.config.system_instruction
        )
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _load_screenshot_cache(self) -> Dict[str, str]:
        """Load screenshot cache from JSON file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                print(f"Error loading screenshot cache from {self.cache_file}, creating new cache")
                return {}
        return {}
    
    def _save_screenshot_cache(self) -> None:
        """Save screenshot cache to JSON file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.screenshot_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving screenshot cache: {str(e)}")
    
    def _normalize_name(self, name: str) -> str:
        """Normalize screenshot name for consistent caching."""
        # Convert to lowercase and remove whitespace
        normalized = name.lower().strip()
        # Replace spaces and special characters with underscores
        normalized = re.sub(r'[^a-z0-9]', '_', normalized)
        # Remove consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        return normalized
    
    def set_video_path(self, video_path: str) -> None:
        """Set the video file path."""
        self.video_path = video_path
    
    def set_video_interpreter(self, video_interpreter: VideoInterpreter) -> None:
        """Set the VideoInterpreter agent."""
        self.video_interpreter = video_interpreter
    
    def process_markdown_file(self, file_path: str, replace_existing: bool = False) -> str:
        """Process a markdown file, replacing screenshot placeholders with actual screenshots."""
        try:
            # Clear the list of unavailable screenshots for this run
            self.unavailable_screenshots = []
            
            # Read the markdown file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix indentation issues by stripping leading whitespace from each line
            lines = content.split('\n')
            fixed_lines = [line.lstrip() for line in lines]
            content = '\n'.join(fixed_lines)
            
            # Fix headers that might not have proper spacing
            content = re.sub(r'^(#+)(\S)', r'\1 \2', content, flags=re.MULTILINE)
            
            # Remove any triple backticks around image markdown to prevent images from being inside code blocks
            content = re.sub(r'```(?:.*?)\s*\n(!\[.*?\]\(.*?\))\s*\n```', r'\1', content)
            content = re.sub(r'```(?:.*?)(!\[.*?\]\(.*?\))```', r'\1', content)
            
            # Define regex pattern to identify screenshot placeholders
            pattern = r'\[SCREENSHOT_PLACEHOLDER\](.*?)\[/SCREENSHOT_PLACEHOLDER\]'
            
            # Find all matches
            matches = re.findall(pattern, content, re.DOTALL)
            
            # Process each match
            for idx, placeholder_content in enumerate(matches):
                try:
                    # Extract the name from the placeholder
                    name_match = re.search(r'Name:\s*(.*?)(?:\n|$)', placeholder_content)
                    
                    if not name_match:
                        print(f"Warning: Screenshot placeholder #{idx+1} does not have a Name attribute, skipping")
                        continue
                    
                    # Get the original name for display
                    screenshot_name_original = name_match.group(1).strip()
                    # Get the normalized name for cache lookup
                    screenshot_name = self._normalize_name(screenshot_name_original)
                    
                    # Build a description for the image alt text
                    # First check if there's any content other than the name
                    has_additional_content = bool(re.search(r'(Purpose|Content|Value):\s*(.*?)(?:\n|$)', placeholder_content))
                    
                    if has_additional_content:
                        # Extract purpose, content, and value if available
                        purpose_match = re.search(r'Purpose:\s*(.*?)(?:\n|$)', placeholder_content)
                        content_match = re.search(r'Content:\s*(.*?)(?:\n|$)', placeholder_content)
                        value_match = re.search(r'Value:\s*(.*?)(?:\n|$)', placeholder_content)
                        
                        # Combine the extracted information into a description
                        description_parts = []
                        if purpose_match:
                            description_parts.append(purpose_match.group(1).strip())
                        if content_match:
                            description_parts.append(content_match.group(1).strip())
                        if value_match:
                            description_parts.append(value_match.group(1).strip())
                        
                        description = " - ".join(description_parts) if description_parts else screenshot_name_original
                    else:
                        # If there's only a name, use it as the description
                        description = screenshot_name_original
                    
                    # Check if we already have this screenshot in our cache
                    screenshot_path = None
                    if not replace_existing and screenshot_name in self.screenshot_cache:
                        cached_path = self.screenshot_cache[screenshot_name]
                        if os.path.exists(cached_path):
                            screenshot_path = cached_path
                            print(f"Using cached screenshot for '{screenshot_name_original}' (normalized: '{screenshot_name}'): {screenshot_path}")
                    
                    # If the screenshot doesn't exist in cache or we're replacing existing ones,
                    # only generate a new one if there's additional content to use
                    if screenshot_path is None:
                        if has_additional_content:
                            # Get timestamp from VideoInterpreter
                            timestamp_hms = None
                            if self.video_interpreter:
                                try:
                                    timestamp_hms = self._get_timestamp_from_interpreter(description)
                                    print(f"Extracted timestamp for new screenshot '{screenshot_name_original}': {timestamp_hms}")
                                except Exception as e:
                                    print(f"Error getting timestamp for new screenshot '{screenshot_name_original}': {str(e)}")
                            
                            if timestamp_hms is None:
                                # Screenshot is not available, add to list and remove placeholder
                                self.unavailable_screenshots.append(screenshot_name_original)
                                placeholder = f'[SCREENSHOT_PLACEHOLDER]{placeholder_content}[/SCREENSHOT_PLACEHOLDER]'
                                content = content.replace(placeholder, '')
                                print(f"Timestamp not available for screenshot: '{screenshot_name_original}', removing placeholder!")
                                continue
                            
                            # Convert HH:MM:SS to seconds
                            h, m, s = map(int, timestamp_hms.split(':'))
                            timestamp_seconds = h * 3600 + m * 60 + s
                            
                            # Take screenshot
                            screenshot_path = self.take_screenshot(timestamp_seconds, screenshot_name)
                            
                            if screenshot_path and os.path.exists(screenshot_path):
                                # Add to cache
                                self.screenshot_cache[screenshot_name] = screenshot_path
                                self._save_screenshot_cache()
                            else:
                                # Screenshot failed to be taken, add to unavailable list
                                self.unavailable_screenshots.append(screenshot_name_original)
                                placeholder = f'[SCREENSHOT_PLACEHOLDER]{placeholder_content}[/SCREENSHOT_PLACEHOLDER]'
                                content = content.replace(placeholder, '')
                                print(f"Screenshot failed to be taken for screenshot: '{screenshot_name_original}', removing placeholder!")
                                continue
                    
                    if screenshot_path and os.path.exists(screenshot_path):
                        # Get relative path for markdown
                        rel_path = os.path.relpath(screenshot_path, os.path.dirname(file_path))
                        
                        # Replace placeholder with actual image in markdown
                        placeholder = f'[SCREENSHOT_PLACEHOLDER]{placeholder_content}[/SCREENSHOT_PLACEHOLDER]'
                        replacement = f'![{description}]({rel_path})'
                        content = content.replace(placeholder, replacement)
                except Exception as e:
                    print(f"Error processing screenshot placeholder #{idx+1}: {str(e)}")
            
            # Ensure images are not inside code blocks by moving them outside
            code_blocks = re.finditer(r'```.*?```', content, re.DOTALL)
            for block in code_blocks:
                block_content = block.group(0)
                # Check if there are any images in this code block
                images = re.findall(r'!\[.*?\]\(.*?\)', block_content)
                if images:
                    # For each image found in the code block
                    for img in images:
                        # Remove the image from the code block
                        new_block = block_content.replace(img, '')
                        # Place the image after the code block
                        content = content.replace(block_content, new_block + '\n\n' + img)
            
            # Save the updated markdown to a new file
            filename_without_ext = os.path.splitext(file_path)[0]
            enhanced_file_path = f"{filename_without_ext}_enhanced.md"
            
            with open(enhanced_file_path, 'w') as f:
                f.write(content)
            
            print(f"Enhanced markdown saved to: {enhanced_file_path}")
            
            return enhanced_file_path
        except Exception as e:
            print(f"Error in process_markdown_file: {str(e)}")
            return file_path  # Return original file path if processing fails
    
    def _get_timestamp_from_interpreter(self, screenshot_description: str) -> Optional[str]:
        """Get the timestamp for a screenshot from the VideoInterpreter."""
        prompt = f"""
        I need to find a frame in the video that is relevant to the following description:
        
        {screenshot_description}
        
        IMPORTANT RULES:
        1. ONLY respond with either:
           - A timestamp in HH:MM:SS format (e.g., "00:05:30") if you can find a relevant frame in the video
           - The exact text "screenshot_not_available" if you cannot find any relevant frames to the description
        2. DO NOT include any explanations or additional text
        3. DO NOT use any other format for timestamps
        4. DO NOT provide partial or uncertain responses
        5. Return "screenshot_not_available" very sparingly and only for cases where you cannot find any relevant frames to the description.
        """
        
        # Get response from VideoInterpreter
        response = self.video_interpreter.respond(prompt)
        
        # Clean up any whitespace and get just the first line
        response = response.strip().split('\n')[0].strip()
        
        # Check if screenshot is not available
        if response.lower() == 'screenshot_not_available':
            return None
        
        # Extract timestamp using regex (looking for HH:MM:SS format)
        timestamp_pattern = r'(\d{1,2}):(\d{2}):(\d{2})'
        match = re.search(timestamp_pattern, response)
        
        if match:
            hours, minutes, seconds = match.groups()
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            # If no timestamp found, try to parse the response as a timestamp
            parts = response.strip().split(':')
            if len(parts) == 3 and all(part.isdigit() for part in parts):
                hours, minutes, seconds = parts
                return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
            # No valid timestamp found
            return None
    
    def take_screenshot(self, timestamp_seconds: int, screenshot_name: str) -> str:
        """Take a screenshot from the video at the specified timestamp and save it to disk."""
        try:
            # Convert seconds to HH:MM:SS format
            hours = timestamp_seconds // 3600
            minutes = (timestamp_seconds % 3600) // 60
            seconds = timestamp_seconds % 60
            timestamp_hms = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Create a unique filename using the name and timestamp
            screenshot_filename = f"screenshot_{screenshot_name}_{int(time.time())}.png"
            
            # Get the screenshot path
            screenshots_dir = os.path.join(self.output_dir, "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
            
            # Extract the screenshot using VideoScreenshotTool
            screenshot = VideoScreenshotTool(self.video_path, timestamp_hms)
            
            # Save the screenshot
            screenshot.save(screenshot_path)
            
            print(f"Screenshot saved to {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Error taking screenshot at {timestamp_seconds} seconds: {str(e)}")
            return None

    def get_unavailable_screenshots(self) -> list:
        """Get the list of screenshots that were not available in the last processed file."""
        return self.unavailable_screenshots


# Example usage
if __name__ == "__main__":
    print("Running ScreenshotAgent example...")
    
    # Create a simple markdown file with screenshot placeholders
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    temp_dir = os.path.join(parent_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    markdown_content = """# Radiographics Tutorial
    ## Step 1: Search for Articles
    [SCREENSHOT_PLACEHOLDER]
    Name: Search Results
    Purpose: Shows a Google search result with "Radiographics Top 10 Articles" query
    Content: The search results page with the RG TEAM Top 10 Reading List appearing as the top result
    Value: Helps the user identify the correct search query and result to click
    [/SCREENSHOT_PLACEHOLDER]

    ## Step 2: Access the Website
    [SCREENSHOT_PLACEHOLDER]
    Name: Website Homepage
    Purpose: Shows the Radiographics website homepage
    Content: The main landing page with navigation menu and featured articles
    Value: Helps the user understand what the website looks like and how to navigate it
    [/SCREENSHOT_PLACEHOLDER]
    
    ## Step 3: Reuse Previous Screenshot
    [SCREENSHOT_PLACEHOLDER]
    Name: Search Results
    [/SCREENSHOT_PLACEHOLDER]
    """
    
    # Create a second markdown file to demonstrate cross-file screenshot reuse
    markdown_content2 = """# Radiographics Quick Guide
    ## Finding Articles Quickly
    [SCREENSHOT_PLACEHOLDER]
    Name: Search Results
    [/SCREENSHOT_PLACEHOLDER]

    ## Exploring New Features
    [SCREENSHOT_PLACEHOLDER]
    Name: website homepage
    [/SCREENSHOT_PLACEHOLDER]
    """
    
    temp_md_path = os.path.join(temp_dir, "tutorial.md")
    with open(temp_md_path, "w") as f:
        f.write(markdown_content)
    
    temp_md_path2 = os.path.join(temp_dir, "quick_guide.md")
    with open(temp_md_path2, "w") as f:
        f.write(markdown_content2)
    
    print(f"Created temporary markdown files in: {temp_dir}")
    
    # Video Path - use a command line argument if provided, otherwise use default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Default video path
        video_path = os.path.join(parent_dir, "data", "RG_Drive_Demonsration.mp4")
    
    print(f"Using video: {video_path}")
    
    # Initialize the VideoInterpreter
    print("Initializing VideoInterpreter...")
    video_interpreter = VideoInterpreter()
    video_interpreter.load_video(video_path)
    
    # Initialize the ScreenshotAgent
    output_dir = os.path.join(os.path.dirname(temp_md_path), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    screenshot_agent = ScreenshotAgent(
        video_interpreter=video_interpreter, 
        video_path=video_path,
        output_dir=output_dir
    )

    # Process the first markdown file
    print("\n*** Processing first markdown file ***")
    enhanced_markdown_path = screenshot_agent.process_markdown_file(temp_md_path)
    
    # Process the second markdown file to demonstrate cross-file screenshot reuse
    print("\n*** Processing second markdown file (demonstrating cross-file screenshot reuse) ***")
    enhanced_markdown_path2 = screenshot_agent.process_markdown_file(temp_md_path2)
    
    print("\nScreenshot cache content:")
    print(f"Cache saved to: {screenshot_agent.cache_file}")
    for name, path in screenshot_agent.screenshot_cache.items():
        print(f"  - '{name}': {path}")