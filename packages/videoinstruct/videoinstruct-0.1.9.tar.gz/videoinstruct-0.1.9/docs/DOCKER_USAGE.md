# Docker Usage Guide for VideoInstruct

This guide covers everything you need to know about using VideoInstruct with Docker.

## Using the Pre-built Image from Docker Hub

### Prerequisites

1. Install Docker:

   - **macOS**: Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - **Windows**: Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - **Linux**: Follow the [Docker Engine installation guide](https://docs.docker.com/engine/install/)

2. Verify Docker installation:

   ```bash
   docker --version
   docker info
   ```

3. Get API Keys:
   - OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
   - Gemini API key from [Google AI Studio](https://makersuite.google.com/)
   - DeepSeek API key from [DeepSeek Platform](https://platform.deepseek.ai/)

### Quick Start

1. Create a `.env` file with your API keys and configuration:

   ```bash
   # Required API Keys
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   DEEPSEEK_API_KEY=your_deepseek_key

   # Optional Configuration (with defaults shown)
   MAX_ITERATIONS=15
   DOC_GENERATOR_MODEL=o3-mini
   DOC_GENERATOR_TEMPERATURE=0.7
   DOC_GENERATOR_MAX_TOKENS=4000
   VIDEO_INTERPRETER_MODEL=gemini-2.0-flash
   VIDEO_INTERPRETER_TEMPERATURE=0.7
   DOC_EVALUATOR_MODEL=deepseek-reasoner
   DOC_EVALUATOR_TEMPERATURE=0.2
   DOC_EVALUATOR_MAX_REJECTIONS=3
   ```

2. Create necessary directories:

   ```bash
   mkdir -p data output temp
   ```

3. Pull the latest VideoInstruct image:

   ```bash
   docker pull videoinstruct/videoinstruct:latest
   ```

4. Run VideoInstruct:

   ```bash
   # With a local video file (place your video in the data directory first)
   docker run --rm \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/output:/app/output" \
     -v "$(pwd)/temp:/app/temp" \
     --env-file .env \
     videoinstruct/videoinstruct:latest \
     --video /app/data/your_video.mp4
   ```

The container will:

- Download the video if a URL is provided
- Process the video using the specified configuration
- Generate documentation in the `output` directory

### Understanding the Docker Command

Let's break down the Docker command:

- `--rm`: Remove the container after it exits
- `-v "$(pwd)/data:/app/data"`: Mount local data directory for video input
- `-v "$(pwd)/output:/app/output"`: Mount local output directory for documentation
- `-v "$(pwd)/temp:/app/temp"`: Mount local temp directory for processing
- `--env-file .env`: Load environment variables from .env file
- `--video`: Specify the video path (inside container) or URL

### Available Configuration Options

| Option                          | Description                           | Default           |
| ------------------------------- | ------------------------------------- | ----------------- |
| `MAX_ITERATIONS`                | Maximum refinement iterations         | 15                |
| `DOC_GENERATOR_MODEL`           | Model for documentation generation    | o3-mini           |
| `DOC_GENERATOR_TEMPERATURE`     | Temperature for doc generation        | 0.7               |
| `DOC_GENERATOR_MAX_TOKENS`      | Max tokens for doc generation         | 4000              |
| `VIDEO_INTERPRETER_MODEL`       | Model for video interpretation        | gemini-2.0-flash  |
| `VIDEO_INTERPRETER_TEMPERATURE` | Temperature for video interpretation  | 0.7               |
| `DOC_EVALUATOR_MODEL`           | Model for doc evaluation              | deepseek-reasoner |
| `DOC_EVALUATOR_TEMPERATURE`     | Temperature for doc evaluation        | 0.2               |
| `DOC_EVALUATOR_MAX_REJECTIONS`  | Max rejections before user escalation | 3                 |

You can override any configuration option by:

1. Setting it in your .env file
2. Passing it as an environment variable to Docker:
   ```bash
   docker run --rm \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/output:/app/output" \
     -v "$(pwd)/temp:/app/temp" \
     --env-file .env \
     -e DOC_GENERATOR_MODEL=gpt-4 \
     -e MAX_ITERATIONS=20 \
     videoinstruct/videoinstruct:latest \
     --video /app/data/your_video.mp4
   ```

## For Developers: Building and Publishing

### Building from Source

If you want to build the Docker image yourself:

1. Prerequisites:

   - All user prerequisites above
   - Git installed on your system
   - Access to GitHub repository

2. Clone the repository:

   ```bash
   git clone https://github.com/PouriaRouzrokh/VideoInstruct.git
   cd VideoInstruct
   ```

3. Build the image:

   ```bash
   # Build with the default tag
   docker build -t videoinstruct/videoinstruct:latest .

   # Or build with a specific version tag
   docker build -t videoinstruct/videoinstruct:1.0.0 .
   ```

The Dockerfile includes:

- Python 3.11 slim base image
- System dependencies (ffmpeg, libsm6, libxext6)
- VideoInstruct package installation
- Support for video download (yt-dlp)
- Default configuration values
- Automatic directory creation
- Entrypoint script for flexible usage

### Testing the Local Build

After building, you can test the image locally:

```bash
# Create necessary directories
mkdir -p data output temp

# Run with a local video
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/temp:/app/temp" \
  --env-file .env \
  videoinstruct:latest \
  --video /app/data/your_video.mp4
```

### Publishing to Docker Hub

1. Login to Docker Hub:

   ```bash
   docker login
   ```

2. Tag your image (if not already tagged):

   ```bash
   docker tag videoinstruct:latest videoinstruct/videoinstruct:latest
   ```

3. Push to Docker Hub:
   ```bash
   docker push videoinstruct/videoinstruct:latest
   ```

For automated builds and publishing, you can use our publish script:

```bash
# Publish a new version
python scripts/publish_docker.py --version 1.0.0

# Build without publishing (for testing)
python scripts/publish_docker.py --no-push
```

## Troubleshooting

### Common Issues

1. Docker Command Not Found

   - Make sure Docker is installed (see [Prerequisites](#prerequisites))
   - On macOS/Linux: Add Docker to your PATH if using custom installation
   - On Windows: Restart your terminal after installation
   - Verify installation with `docker --version`

2. Docker Desktop Not Running

   - Start Docker Desktop application
   - Wait for the Docker engine to fully start
   - Verify with `docker info`

3. Permission Errors

   ```bash
   # Fix permissions on mounted directories
   chmod 777 data output temp

   # On Linux, you might need to run Docker with sudo or add your user to the docker group:
   sudo usermod -aG docker $USER  # Remember to log out and back in
   ```

4. Video Download Issues

   - Check if the URL is accessible
   - Try downloading the video manually to the data directory

5. Container Start Failures

   - Check if required ports are available
   - Ensure you have enough disk space
   - Check Docker logs: `docker logs <container_id>`

6. API Call Issues

   - Verify your API keys in the .env file
   - Check if you have sufficient credits/quota
   - Ensure your .env file is properly mounted

7. Image Pull Issues
   - Check your internet connection
   - Verify Docker Hub is accessible
   - Try pulling with explicit version: `docker pull videoinstruct/videoinstruct:latest`
   - If Docker Hub is down, build locally using instructions above
