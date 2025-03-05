# VideoInstruct

VideoInstruct is a tool that automatically generates step-by-step documentation from instructional videos. It uses AI to extract transcriptions, interpret video content, and create comprehensive markdown guides.

## Pipeline:

<img src="Figure.png" width="900" alt="VideoInstruct Pipeline">

VideoInstruct employs a sophisticated pipeline that transforms instructional videos into comprehensive documentation through multiple AI-powered stages. The process begins with the Video Interpreter, which simultaneously handles video transcription extraction and visual content analysis. This dual-stream approach ensures both spoken instructions and visual demonstrations are captured. The extracted information is then fed into the Documentation Generator, which creates structured, step-by-step documentation. Before finalization, the Documentation Evaluator assesses the quality and completeness of the generated content using conversation memory and interactive Q&A between AI agents. If the documentation doesn't meet the defined standards, it's sent back for refinement, ensuring high-quality output that accurately represents the video's instructional content.

## Quick Start

### Using Docker (Recommended)

The fastest and simplest way to use VideoInstruct is through our Docker image. See [DOCKER_USAGE.md](DOCKER_USAGE.md) for detailed instructions on:

- Installation and prerequisites
- Downloading the Docker file from Docker Hub.
- Configuration options
- Troubleshooting common issues

### Using Python Package

```bash
# Install from PyPI
pip install videoinstruct

# Set up environment variables
export OPENAI_API_KEY=your_openai_key
export GEMINI_API_KEY=your_gemini_key
export DEEPSEEK_API_KEY=your_deepseek_key

# Use in your code
from videoinstruct import VideoInstructor
instructor = VideoInstructor(video_path="path/to/video.mp4")
documentation = instructor.generate_documentation()
```

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

## Installation Options

1. **Docker (Recommended)**: See [DOCKER_USAGE.md](DOCKER_USAGE.md)
2. **PyPI**: `pip install videoinstruct`
3. **Source**:
   ```bash
   git clone https://github.com/PouriaRouzrokh/VideoInstruct.git
   cd VideoInstruct
   pip install -r requirements.txt
   ```

## Project Structure

```
VideoInstruct/
├── data/                  # Place your video files here
├── docs/                  # Documentation files
│   ├── README.md         # Main documentation
│   ├── DOCKER_USAGE.md   # Docker setup guide
│   └── Figure.png        # Pipeline diagram
├── examples/              # Example usage scripts
│   └── example_usage.py  # Basic usage example
├── output/               # Generated documentation output
├── scripts/              # Utility scripts
├── temp/                 # Temporary files directory
├── videoinstruct/        # Main package
│   ├── agents/          # AI agent modules
│   ├── prompts/         # System prompts for agents
│   ├── tools/           # Utility tools
│   ├── utils/           # Utility functions
│   ├── __init__.py      # Package initialization
│   ├── configs.py       # Configuration classes
│   ├── prompt_loader.py # Prompt loading utilities
│   └── videoinstructor.py # Main orchestration class
├── Dockerfile           # Docker configuration
├── LICENSE              # MIT License
├── MANIFEST.in         # Package manifest
├── pyproject.toml      # Project metadata
├── requirements.txt    # Python dependencies
└── setup.py           # Package setup script
```

## Using as a Python Package

```python
from videoinstruct import VideoInstructor, VideoInstructorConfig
from videoinstruct.agents import DocGeneratorConfig, VideoInterpreterConfig, DocEvaluatorConfig

# Configure the VideoInstructor
config = VideoInstructorConfig(
    doc_generator_config=DocGeneratorConfig(
        api_key=openai_api_key,
        model_provider="openai",
        model="o3-mini",
        temperature=0.7
    ),
    video_interpreter_config=VideoInterpreterConfig(
        api_key=gemini_api_key,
        model="gemini-2.0-flash"
    ),
    doc_evaluator_config=DocEvaluatorConfig(
        api_key=deepseek_api_key,
        model="deepseek-reasoner"
    )
)

# Initialize and run
instructor = VideoInstructor(
    video_path="path/to/video.mp4",
    config=config
)
documentation = instructor.generate_documentation()
```

## Contributing

To contribute to VideoInstruct:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Troubleshooting

- For Docker-related issues, see [DOCKER_USAGE.md](DOCKER_USAGE.md#troubleshooting)
- For Python package issues:
  - Make sure all dependencies are installed
  - Check your Python version (3.8+ required)
  - Verify your API keys and internet connection

## License

[MIT License](LICENSE)
