# VideoInstruct

VideoInstruct is a tool that automatically generates step-by-step documentation from instructional videos. It uses AI to extract transcriptions, interpret video content, and create comprehensive markdown guides.

## Features

- Automatic video transcription extraction
- AI-powered video interpretation
- Step-by-step documentation generation
- Automated documentation quality evaluation with conversation memory
- Interactive Q&A workflow between AI agents
- User feedback integration for documentation refinement
- Configurable escalation to human users
- Screenshot generation and annotation
- PDF export capabilities
- Enhanced workflow visibility with real-time status updates
- Transparent model information display for each agent

## Workflow Information

When running VideoInstruct, you'll see detailed information about:

1. Current AI models powering each agent:

   - DocGenerator model and provider
   - VideoInterpreter model (Google Gemini)
   - DocEvaluator model and provider

2. Step-by-step workflow breakdown:

   - Video transcription extraction
   - Detailed video interpretation
   - Documentation generation
   - Documentation review and evaluation
   - Quality assessment with feedback
   - User interaction points

3. Progress tracking:
   - Documentation versions
   - Evaluation results
   - Screenshot processing status
   - PDF generation status

## Project Structure

```
VideoInstruct/
├── data/                  # Place your video files here
├── examples/              # Example usage scripts
│   ├── example_usage.py   # Basic example with repository structure
├── output/                # Generated documentation output
├── videoinstruct/         # Main package
│   ├── agents/            # AI agent modules
│   │   ├── DocGenerator.py      # Documentation generation agent
│   │   ├── DocEvaluator.py      # Documentation evaluation agent
│   │   ├── VideoInterpreter.py  # Video interpretation agent
│   │   └── ScreenshotAgent.py   # Screenshot generation agent
│   ├── prompts/           # System prompts for agents
│   ├── tools/             # Utility tools
│   │   ├── image_annotator.py   # Image annotation tools
│   │   └── video_screenshot.py  # Video screenshot tools
│   ├── utils/             # Utility functions
│   │   ├── transcription.py     # Video transcription utilities
│   │   └── md2pdf.py            # Markdown to PDF conversion
│   ├── cli.py             # Command-line interface
│   ├── configs.py         # Configuration classes
│   ├── prompt_loader.py   # Prompt loading utilities
│   └── videoinstructor.py # Main orchestration class
├── .env                   # Environment variables (API keys)
├── MANIFEST.in            # Package manifest file
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Package dependencies
├── setup.py               # Package setup file
└── README.md              # This file
```

## Requirements

- Python 3.8+
- OpenAI API key (for DocGenerator)
- Google Gemini API key (for VideoInterpreter)
- DeepSeek API key (for DocEvaluator)
- FFmpeg (for video processing)

## Installation

### From PyPI

```bash
pip install videoinstruct
```

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/VideoInstruct.git
   cd VideoInstruct
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables in `.env`:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_gemini_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

## Usage

### Basic Usage

```python
from videoinstruct import VideoInstructor, VideoInstructorConfig

# Initialize VideoInstructor with your video
instructor = VideoInstructor(video_path="path/to/your/video.mp4")

# Generate documentation
documentation_path = instructor.generate_documentation()
```

When you run the documentation generation, you'll see informative output like this:

```
==================================================
STARTING DOCUMENTATION GENERATION
==================================================
Generating documentation for video: your_video.mp4
----------------------------------------------------------------------------------------------------
Here are the current models empowering the agents:
DocGenerator:  openai gpt-4
VideoInterpreter:  google gemini-2.0-flash
DocEvaluator:  deepseek deepseek-reasoner
----------------------------------------------------------------------------------------------------

Workflow:
1. Video transcription will be extracted
2. VideoInterpreter will provide a detailed description
3. DocGenerator will create step-by-step documentation
4. Generated documentation will be shown to you before evaluation
5. DocEvaluator will assess documentation quality
   - Will provide feedback on each evaluation round
   - Will escalate to user after 3 rejections
6. You'll be asked for feedback at certain intervals
----------------------------------------------------------------------------------------------------
```

## Using as a Python Package

You can use VideoInstruct as a Python package in your own projects:

```python
from videoinstruct import VideoInstructor, VideoInstructorConfig
from videoinstruct.agents.DocGenerator import DocGeneratorConfig
from videoinstruct.agents.VideoInterpreter import VideoInterpreterConfig
from videoinstruct.agents.DocEvaluator import DocEvaluatorConfig
from pathlib import Path

# Configure the VideoInstructor
config = VideoInstructorConfig(
   # DocGenerator configuration
   doc_generator_config=DocGeneratorConfig(
      api_key=openai_api_key,
      model_provider="openai",
      model="o3-mini",
      temperature=0.7,
      max_output_tokens=4000
   ),

   # VideoInterpreter configuration
   video_interpreter_config=VideoInterpreterConfig(
      api_key=gemini_api_key,
      model="gemini-2.0-flash",  # You can change this to any supported Gemini model
      temperature=0.7
   ),

   # DocEvaluator configuration
   doc_evaluator_config=DocEvaluatorConfig(
      api_key=deepseek_api_key,
      model_provider="deepseek",
      model="deepseek-reasoner",
      temperature=0.2,
      max_rejection_count=3  # Number of rejections before escalating to user
   ),

   # VideoInstructor configuration
   max_iterations=15,
   output_dir="output",
   temp_dir="temp"
)

# Path to the video file - replace with your video file name
video_path = "test.mp4"  # Updated to match the actual file name

# Initialize VideoInstructor
instructor = VideoInstructor(
   video_path=video_path,
   config=config
)

# Generate documentation
documentation = instructor.generate_documentation()
```

## Workflow

VideoInstruct follows this workflow:

1. **Transcription**: Extract text from the video
2. **Initial Description**: Get a detailed visual description from VideoInterpreter
3. **Documentation Generation**: DocGenerator creates initial documentation
4. **User Preview**: Generated documentation is shown to the user before evaluation
5. **Documentation Evaluation**: DocEvaluator assesses documentation quality
   - Provides feedback on each evaluation round
   - Maintains conversation memory for context-aware evaluation
   - Escalates to human user after a configurable number of rejections
6. **Refinement**: Documentation is refined based on evaluator feedback
7. **User Feedback**: User provides final approval or additional feedback
8. **Output**: Final documentation is saved as markdown and optionally as PDF

## Development

To contribute to VideoInstruct:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[MIT License](LICENSE)

## Configuration Options

VideoInstruct offers extensive configuration options for each component through its configuration classes. Here's a detailed breakdown:

### Main Configuration (VideoInstructorConfig)

The main configuration class that orchestrates all components:

```python
config = VideoInstructorConfig(
    max_iterations=10,          # Maximum refinement iterations
    output_dir="output",        # Output directory for documentation
    temp_dir="temp",           # Temporary file directory
    generate_pdf_for_all_versions=True  # Generate PDFs for all versions
)
```

### DocGenerator Configuration

Controls how documentation is generated:

```python
doc_generator_config = DocGeneratorConfig(
    model_provider="openai",    # AI provider (openai, anthropic, etc.)
    model="o3-mini",           # Model to use
    temperature=0.7,           # Creativity vs consistency (0-1)
    max_output_tokens=4000,    # Max response length
    stream=False,              # Stream responses
    response_format={"type": "json_object"}  # Response format
)
```

### VideoInterpreter Configuration

Controls video analysis settings:

```python
video_interpreter_config = VideoInterpreterConfig(
    model="gemini-2.0-flash",  # Gemini model for video analysis
    temperature=0.7,           # Analysis randomness
    max_output_tokens=None,    # Max response length
    top_k=None,               # Top-k sampling
    top_p=None                # Nucleus sampling
)
```

### DocEvaluator Configuration

Controls documentation quality assessment:

```python
doc_evaluator_config = DocEvaluatorConfig(
    model_provider="deepseek",  # AI provider
    model="deepseek-reasoner", # Model for evaluation
    temperature=0.2,           # Low temp for consistent evaluation
    max_rejection_count=3      # Max rejections before user escalation
)
```

### Screenshot Agent Configuration

Controls screenshot generation and analysis:

```python
screenshot_agent_config = ScreenshotAgentConfig(
    model="gemini-2.0-flash",  # Model for image analysis
    temperature=0.2,           # Low temp for consistent analysis
    max_output_tokens=None     # Max response length
)
```

### Environment Variables

The following environment variables can be set in your `.env` file:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Optional Configuration
VIDEOINSTRUCT_OUTPUT_DIR=custom_output_dir
VIDEOINSTRUCT_TEMP_DIR=custom_temp_dir
VIDEOINSTRUCT_MAX_ITERATIONS=15
```
