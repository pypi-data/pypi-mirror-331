import os
import datetime
import json
import re
import shutil
from typing import Optional, Tuple

from videoinstruct.agents.VideoInterpreter import VideoInterpreter
from videoinstruct.agents.DocGenerator import DocGenerator
from videoinstruct.agents.DocEvaluator import DocEvaluator
from videoinstruct.agents.ScreenshotAgent import ScreenshotAgent
from videoinstruct.utils.transcription import transcribe_video
from videoinstruct.utils.md2pdf import markdown_to_pdf, clean_markdown
from videoinstruct.configs import (
    ResponseType,
    DocGeneratorResponse,
    VideoInstructorConfig
)


class VideoInstructor:
    """Orchestrates the workflow between DocGenerator, VideoInterpreter, DocEvaluator, and ScreenshotAgent."""
    
    def __init__(
        self,
        video_path: Optional[str] = None,
        transcription_path: Optional[str] = None,
        config: Optional[VideoInstructorConfig] = None
    ):
        """Initialize the VideoInstructor with video path, transcription path and configuration."""
        self.video_path = video_path
        self.transcription_path = transcription_path
        self.transcription = None
        self.config = config or VideoInstructorConfig()
        
        # Create output and temp directories
        if not os.path.exists(self.config.output_dir):
            os.makedirs(self.config.output_dir)
        if not os.path.exists(self.config.temp_dir):
            os.makedirs(self.config.temp_dir)
        
        # Create a timestamped directory for this session
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.config.output_dir, self.timestamp)
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Initialize agents
        self.doc_generator = DocGenerator(
            config=self.config.doc_generator_config,
            output_dir=self.session_dir
        )
        
        self.video_interpreter = VideoInterpreter(
            config=self.config.video_interpreter_config
        )
        
        self.doc_evaluator = DocEvaluator(
            config=self.config.doc_evaluator_config
        )
        
        self.screenshot_agent = ScreenshotAgent(
            config=self.config.screenshot_agent_config,
            video_interpreter=self.video_interpreter,
            video_path=self.video_path,
            output_dir=self.session_dir
        )
        
        # Track document versions
        self.doc_version = 0
        
        # Load video and transcription if provided
        if video_path:
            self.load_video(video_path)
            
        if transcription_path:
            self.load_transcription(transcription_path)
    
    def load_video(self, video_path: str) -> None:
        """Load a video file and extract its transcription."""
        print(f"Loading video from {video_path}...")
        self.video_path = video_path
        
        # Update video path for ScreenshotAgent
        self.screenshot_agent.set_video_path(video_path)
        
        # Load video into VideoInterpreter
        self.video_interpreter.load_video(video_path)
        
        # Extract transcription if not already provided
        if not self.transcription:
            self._extract_transcription()
    
    def load_transcription(self, transcription_path: str) -> None:
        """Load an existing transcription file."""
        print(f"Loading transcription from {transcription_path}...")
        self.transcription_path = transcription_path
        
        with open(transcription_path, 'r') as file:
            self.transcription = file.read()
        
        # Set transcription in DocGenerator
        self.doc_generator.set_transcription(self.transcription)
    
    def _extract_transcription(self) -> None:
        """Extract transcription from the loaded video."""
        if not self.video_path:
            raise ValueError("No video loaded. Please load a video first.")
        
        # Generate a default transcription path if not provided
        if not self.transcription_path:
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            self.transcription_path = os.path.join(self.config.output_dir, f"{video_name}_transcription.txt")
        
        # Check if transcription file already exists
        if os.path.exists(self.transcription_path):
            self.load_transcription(self.transcription_path)
            return
        
        print("Extracting transcription from video...")
        
        # Extract transcription
        success = transcribe_video(
            video_path=self.video_path,
            output_path=self.transcription_path,
            temp_path=self.config.temp_dir
        )
        
        if success:
            with open(self.transcription_path, 'r') as file:
                self.transcription = file.read()
            self.doc_generator.set_transcription(self.transcription)
        else:
            raise ValueError("Failed to extract transcription from video.")
    
    def _get_structured_response(self, response: str) -> DocGeneratorResponse:
        """Parse response from DocGenerator to determine if it's a question or documentation."""
        # Check if the response is in JSON format
        try:
            json_response = json.loads(response)
            if isinstance(json_response, dict) and "type" in json_response and "content" in json_response:
                if json_response["type"] not in [ResponseType.DOCUMENTATION, ResponseType.QUESTION]:
                    json_response["type"] = ResponseType.DOCUMENTATION
                return DocGeneratorResponse(**json_response)
        except json.JSONDecodeError:
            pass
        
        # Use heuristics to determine if it's a question or documentation
        question_patterns = [
            r'\?\s*$',  # Ends with question mark
            r'^(?:can|could|what|when|where|which|who|why|how)',  # Starts with question word
            r'I need more information about',
            r'Please provide more details',
            r'Can you clarify',
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return DocGeneratorResponse(type=ResponseType.QUESTION, content=response)
        
        # If it contains markdown headers, it's likely documentation
        if re.search(r'^#\s+', response, re.MULTILINE):
            return DocGeneratorResponse(type=ResponseType.DOCUMENTATION, content=response)
        
        # Default to documentation
        return DocGeneratorResponse(type=ResponseType.DOCUMENTATION, content=response)
    
    def _save_documentation(self, documentation: str, is_final: bool = False) -> Tuple[str, list]:
        """Save documentation to a file and process screenshots."""
        # Increment version number if not final
        if not is_final:
            self.doc_version += 1
            
        # Create a filename based on version number
        version_suffix = "_final" if is_final else f"_v{self.doc_version}"
        filename = f"documentation{version_suffix}.md"
        raw_documentation_path = os.path.join(self.session_dir, filename)
        
        # Save the documentation to a file
        with open(raw_documentation_path, 'w') as f:
            f.write(documentation)
        
        # Process screenshots
        screenshot_pattern = r'\[SCREENSHOT_PLACEHOLDER\](.*?)\[/SCREENSHOT_PLACEHOLDER\]'
        screenshot_matches = list(re.finditer(screenshot_pattern, documentation, re.DOTALL))
        
        if screenshot_matches:
            print(f"\nProcessing {len(screenshot_matches)} screenshots...")
            processed_documentation_path = self.screenshot_agent.process_markdown_file(raw_documentation_path)
            # Get list of unavailable screenshots
            unavailable_screenshots = self.screenshot_agent.get_unavailable_screenshots()
        else:
            processed_documentation_path = raw_documentation_path
            unavailable_screenshots = []
            
        # Generate PDF
        if self.config.generate_pdf_for_all_versions or is_final:
            self._generate_pdf(processed_documentation_path)
            
        return processed_documentation_path, raw_documentation_path, unavailable_screenshots
    
    def _generate_pdf(self, markdown_path: str) -> str:
        """Generate a PDF from a Markdown file."""
        # Read the markdown content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Clean the Markdown text
        cleaned_md_text = clean_markdown(md_text)
        
        # Define the output PDF path
        pdf_path = f"{os.path.splitext(markdown_path)[0]}.pdf"
        
        # Determine the base directory from the Markdown file's absolute path
        base_path = os.path.dirname(os.path.abspath(markdown_path))
        
        # Generate the PDF
        markdown_to_pdf(cleaned_md_text, pdf_path, base_path)
        
        return pdf_path if os.path.exists(pdf_path) else None
    
    def _evaluate_documentation(self, documentation_path: str, unavailable_screenshots: list) -> Tuple[bool, str]:
        """Evaluate the documentation using the DocEvaluator."""
        print("\n" + "="*50)
        print("EVALUATING DOCUMENTATION...")
        print("="*50)
        
        with open(documentation_path, 'r', encoding='utf-8') as f:
            documentation = f.read()
        
        is_approved, feedback = self.doc_evaluator.evaluate_documentation(documentation, unavailable_screenshots)
        
        if is_approved:
            print("Documentation APPROVED by DocEvaluator")
        else:
            print("Documentation REJECTED by DocEvaluator")
            print(f"Rejection count: {self.doc_evaluator.rejection_count}/{self.doc_evaluator.config.max_rejection_count}")
            
            if self.doc_evaluator.should_escalate_to_user():
                print("Maximum rejections reached. Will escalate to user.")
        
        return is_approved, feedback
    
    def _get_user_feedback(self) -> Tuple[str, bool]:
        """Get feedback from the user about the documentation."""
        # Show the most recent feedback if available
        most_recent_feedback = ""
        if self.doc_evaluator.feedback_history and len(self.doc_evaluator.feedback_history) > 0:
            most_recent_feedback = self.doc_evaluator.feedback_history[-1]
        
        while True:
            user_input = input("\nAre you satisfied with this documentation? (yes/no): ").strip().lower()
            if user_input in ['yes', 'y']:                    
                return "", True
            elif user_input in ['no', 'n']:
                feedback = input("Please provide feedback to improve the documentation (press Enter to use evaluator's feedback): ")
                # If user just presses Enter, use the most recent feedback from the evaluator
                if not feedback.strip() and most_recent_feedback:
                    return most_recent_feedback, False
                return feedback, False
            else:
                print("Please answer 'yes' or 'no'.")
    
    def _handle_user_question(self, question: str) -> str:
        """Let the user answer a question instead of the VideoInterpreter."""
        print("\n" + "="*50)
        print("QUESTION FROM DOC GENERATOR:")
        print("="*50)
        print(question)
        
        user_answer = input("\nPlease answer this question (or type 'interpreter' to let the VideoInterpreter answer): ")
        
        if user_answer.strip().lower() == 'interpreter':
            return self.video_interpreter.respond(question)
        
        return user_answer
    
    def _prepare_initial_prompt(self) -> str:
        """Prepare the initial prompt for documentation generation."""
        print("\n" + "="*50)
        print("PREPARING INITIAL PROMPT")
        print("="*50)
        
        # Get initial description from VideoInterpreter
        initial_description = self.video_interpreter.respond(
            "Please provide a detailed step-by-step description of what is happening in this video. "
            "Focus on the actions being performed, the sequence of steps, and any important visual details. "
            "Be as specific and comprehensive as possible."
        )
        
        # Prepare the prompt
        initial_prompt = f"""
        You will be creating a step-by-step guide based on a video.
        
        Here is the transcription of the video:
        
        TRANSCRIPTION:
        {self.transcription}
        
        Additionally, here is a detailed description of what happens in the video:
        
        VIDEO DESCRIPTION:
        {initial_description}
        
        Using both the transcription and the video description, create a comprehensive step-by-step guide.
        If you have any questions or need clarification about specific parts of the video, please ask.
        """
        
        return initial_prompt
    
    def generate_documentation(self) -> Tuple[str, list]:
        """Generate step-by-step documentation from the loaded video."""
        if not self.transcription:
            raise ValueError("No transcription available. Please load a video or transcription first.")

        # Print workflow information
        print("\n" + "="*50)
        print("STARTING DOCUMENTATION GENERATION")
        print("="*50)
        
        video_name = os.path.basename(self.video_path) if self.video_path else "Unknown video"
        print(f"Generating documentation for video: {video_name}")
        print("-"*100)
        print("Here are the current models empowering the agents:")
        print("DocGenerator: ", self.doc_generator.model_provider, self.doc_generator.config.model)
        print("VideoInterpreter: ", "google", self.video_interpreter.config.model)
        print("DocEvaluator: ", self.doc_evaluator.model_provider, self.doc_evaluator.config.model)
        print("-"*100)
        print("\nWorkflow:")
        print("1. Video transcription will be extracted")
        print("2. VideoInterpreter will provide a detailed description")
        print("3. DocGenerator will create step-by-step documentation")
        print("4. Generated documentation will be shown to you before evaluation")
        print("5. DocEvaluator will assess documentation quality")
        print("   - Will provide feedback on each evaluation round")
        print("   - Will escalate to user after 3 rejections")
        print("6. You'll be asked for feedback at certain intervals")
        print("-"*100)
        print("\nStarting the process...\n")

        # Reset DocEvaluator memory and document version counter
        self.doc_evaluator.reset_memory()
        self.doc_version = 0
        
        # Prepare the initial prompt
        initial_prompt = self._prepare_initial_prompt()
        
        # Initialize counters
        iteration_count = 0
        question_count = 0
        current_documentation = None
        current_documentation_path = None
        is_satisfied = False
        
        # Start the documentation generation process
        response = self.doc_generator.generate_documentation_with_description(initial_prompt)
        structured_response = self._get_structured_response(response)
        
        while iteration_count < self.config.max_iterations and not is_satisfied:
            iteration_count += 1
            
            if structured_response.type == ResponseType.QUESTION:
                question_count += 1
                question = structured_response.content
                
                print(f"\nQuestion from DocGenerator ({question_count}):")
                print(question)
                answer = self.video_interpreter.respond(question)
                print(f"Answer from VideoInterpreter:")
                print(answer)
                
                # Send the answer back to DocGenerator
                response = self.doc_generator.refine_documentation(f"ANSWER: {answer}")
                structured_response = self._get_structured_response(response)
            
            elif structured_response.type == ResponseType.DOCUMENTATION:
                current_documentation = structured_response.content
                
                print("\n" + "="*50)
                print(f"DOCUMENTATION VERSION {self.doc_version + 1}")
                print("="*50)
                print(current_documentation)
                
                # Save the current version of the documentation
                processed_documentation_path, raw_documentation_path, current_unavailable_screenshots = self._save_documentation(current_documentation)

                # Let the DocEvaluator evaluate the documentation
                is_approved, feedback = self._evaluate_documentation(raw_documentation_path, current_unavailable_screenshots)
                
                print(f"Evaluator's feedback: {feedback}")

                # Check if we should escalate to user due to repeated rejections
                if not is_approved and self.doc_evaluator.should_escalate_to_user():
                    print("\n" + "="*50)
                    print("ESCALATING TO USER: DocEvaluator has rejected the documentation multiple times.")
                    print("="*50)
                    user_feedback, is_satisfied = self._get_user_feedback()
                    
                    # Reset the rejection count after user intervention
                    self.doc_evaluator.reset_rejection_count()
                    
                    if not is_satisfied and user_feedback:
                        # Refine documentation based on user feedback
                        response = self.doc_generator.refine_documentation(user_feedback)
                        structured_response = self._get_structured_response(response)
                    elif is_satisfied:
                        # User is satisfied, break the loop
                        break
                
                # If DocEvaluator approved or we're continuing after rejection
                elif is_approved:
                    # DocEvaluator approved, now get user feedback
                    user_feedback, is_satisfied = self._get_user_feedback()
                    
                    if not is_satisfied and user_feedback:
                        # Refine documentation based on user feedback
                        response = self.doc_generator.refine_documentation(user_feedback)
                        structured_response = self._get_structured_response(response)
                    elif is_satisfied:
                        break
                else:
                    # DocEvaluator rejected, refine based on feedback
                    response = self.doc_generator.refine_documentation(feedback)
                    structured_response = self._get_structured_response(response)
            
            else:
                raise ValueError(f"Unknown response type: {structured_response.type}")
        
        if iteration_count >= self.config.max_iterations:
            print("\nReached maximum number of iterations without achieving satisfaction.")
        else:
            print("\nDocumentation generation completed successfully. The final documentation is saved at:")
            print(os.path.splitext(processed_documentation_path)[0] + ".pdf")
        
        # Return the final documentation path 
        return processed_documentation_path