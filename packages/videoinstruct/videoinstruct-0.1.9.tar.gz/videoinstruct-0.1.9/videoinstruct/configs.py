from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field

from videoinstruct.prompt_loader import (
    DOC_GENERATOR_SYSTEM_PROMPT, 
    DOC_EVALUATOR_SYSTEM_PROMPT,
    SCREENSHOT_AGENT_SYSTEM_PROMPT
)


class VideoInterpreterConfig(BaseModel):
    """Configuration for the VideoInterpreter class.
    
    This class handles configuration for the video interpretation component that uses
    Google's Gemini model to analyze and understand video content.

    Attributes:
        api_key (Optional[str]): Google Gemini API key. If None, will try to use environment variable.
        model (str): The Gemini model to use. Defaults to "gemini-2.0-flash" for fast processing.
        system_instruction (Optional[str]): Custom system prompt for the model.
        max_output_tokens (Optional[int]): Maximum number of tokens in model response.
        top_k (Optional[int]): Number of highest probability tokens to consider.
        top_p (Optional[float]): Cumulative probability cutoff for token sampling.
        temperature (Optional[float]): Sampling temperature, higher means more random.
        response_mime_type (Optional[str]): Expected MIME type of the response.
        stop_sequences (Optional[List[str]]): Sequences where the model should stop generating.
        seed (Optional[int]): Random seed for reproducible results.
    """
    api_key: Optional[str] = None
    model: str = Field(default="gemini-2.0-flash")
    system_instruction: Optional[str] = None
    max_output_tokens: Optional[int] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    response_mime_type: Optional[str] = None
    stop_sequences: Optional[List[str]] = None
    seed: Optional[int] = None


class DocGeneratorConfig(BaseModel):
    """Configuration for the DocGenerator class.
    
    This class handles configuration for the documentation generation component that
    converts video interpretations into structured documentation.

    Attributes:
        api_key (Optional[str]): OpenAI API key. If None, will try to use environment variable.
        model_provider (str): The AI provider to use (default: "openai").
        model (str): The model to use (default: "o3-mini" for optimal performance/cost).
        system_instruction (str): System prompt that guides documentation generation.
        max_output_tokens (Optional[int]): Maximum number of tokens in model response.
        temperature (float): Controls randomness in generation (0.7 balances creativity/consistency).
        top_p (Optional[float]): Nucleus sampling parameter.
        stream (bool): Whether to stream the model's response.
        seed (Optional[int]): Random seed for reproducible results.
        response_format (Optional[Dict[str, Any]]): Expected format of model response.
    """
    api_key: Optional[str] = None
    model_provider: str = Field(default="openai")
    model: str = Field(default="o3-mini")
    system_instruction: str = Field(default=DOC_GENERATOR_SYSTEM_PROMPT)
    max_output_tokens: Optional[int] = None
    temperature: float = Field(default=0.7)
    top_p: Optional[float] = None
    stream: bool = Field(default=False)
    seed: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = Field(default={"type": "json_object"})


class DocEvaluatorConfig(BaseModel):
    """Configuration for the DocEvaluator class.
    
    This class handles configuration for the documentation evaluation component that
    assesses and provides feedback on generated documentation quality.

    Attributes:
        api_key (Optional[str]): DeepSeek API key. If None, will try to use environment variable.
        model_provider (str): The AI provider to use (default: "deepseek").
        model (str): The model to use (default: "deepseek-reasoner" for evaluation).
        system_instruction (str): System prompt that guides evaluation process.
        max_output_tokens (Optional[int]): Maximum number of tokens in model response.
        temperature (float): Low temperature (0.2) for consistent evaluation.
        top_p (Optional[float]): Nucleus sampling parameter.
        stream (bool): Whether to stream the model's response.
        seed (Optional[int]): Random seed for reproducible results.
        max_rejection_count (int): Max times doc can be rejected before user escalation.
    """
    api_key: Optional[str] = None
    model_provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-reasoner")
    system_instruction: str = Field(default=DOC_EVALUATOR_SYSTEM_PROMPT)
    max_output_tokens: Optional[int] = None
    temperature: float = Field(default=0.2)
    top_p: Optional[float] = None
    stream: bool = Field(default=False)
    seed: Optional[int] = None
    max_rejection_count: int = Field(default=3)


class ScreenshotAgentConfig(BaseModel):
    """Configuration for the ScreenshotAgent class.
    
    This class handles configuration for the screenshot processing component that
    generates and annotates video screenshots for documentation.

    Attributes:
        api_key (Optional[str]): Gemini API key. If None, will try to use environment variable.
        model (str): The model to use (default: "gemini-2.0-flash" for vision tasks).
        system_instruction (str): System prompt that guides screenshot analysis.
        max_output_tokens (Optional[int]): Maximum number of tokens in model response.
        temperature (float): Low temperature (0.2) for consistent analysis.
        top_p (Optional[float]): Nucleus sampling parameter.
        top_k (Optional[int]): Top-k sampling parameter.
        seed (Optional[int]): Random seed for reproducible results.
    """
    api_key: Optional[str] = None
    model: str = Field(default="gemini-2.0-flash")
    system_instruction: str = Field(default=SCREENSHOT_AGENT_SYSTEM_PROMPT)
    max_output_tokens: Optional[int] = None
    temperature: float = Field(default=0.2)
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    seed: Optional[int] = None


class ResponseType(BaseModel):
    """Enum-like class for response types from DocGenerator."""
    DOCUMENTATION: ClassVar[str] = "documentation"
    QUESTION: ClassVar[str] = "question"


class DocGeneratorResponse(BaseModel):
    """Structured response from DocGenerator."""
    type: str  # One of ResponseType values
    content: str  # Documentation content or question
    confidence: Optional[float] = None  # Confidence level (0-1) if applicable


class VideoInstructorConfig(BaseModel):
    """Configuration for the VideoInstructor class.
    
    This is the main configuration class that orchestrates all components of the
    VideoInstruct system. It combines configurations for document generation,
    video interpretation, evaluation, and screenshot processing.

    Attributes:
        doc_generator_config (DocGeneratorConfig): Configuration for documentation generation.
        video_interpreter_config (VideoInterpreterConfig): Configuration for video interpretation.
        doc_evaluator_config (DocEvaluatorConfig): Configuration for documentation evaluation.
        screenshot_agent_config (ScreenshotAgentConfig): Configuration for screenshot processing.
        max_iterations (int): Maximum number of refinement iterations (default: 10).
        output_dir (str): Directory for final documentation output (default: "output").
        temp_dir (str): Directory for temporary files (default: "temp").
        generate_pdf_for_all_versions (bool): Whether to generate PDFs for all doc versions.
    """
    doc_generator_config: DocGeneratorConfig = Field(default_factory=DocGeneratorConfig)
    video_interpreter_config: VideoInterpreterConfig = Field(default_factory=VideoInterpreterConfig)
    doc_evaluator_config: DocEvaluatorConfig = Field(default_factory=DocEvaluatorConfig)
    screenshot_agent_config: ScreenshotAgentConfig = Field(default_factory=ScreenshotAgentConfig)
    max_iterations: int = Field(default=10)
    output_dir: str = Field(default="output")
    temp_dir: str = Field(default="temp")
    generate_pdf_for_all_versions: bool = Field(default=True)  # Whether to generate PDFs for all versions, not just final 