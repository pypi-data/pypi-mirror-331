# LlamaCloud Python LlamaCloud

A Python client for interacting with the LlamaCloud AI APIs for image and video generation.

## Installation

```bash
pip install llamacloud-python
```

## Usage

### Authentication

You can authenticate using an API key directly or via an environment variable:

```python
from llamacloud import LlamaCloud

# Option 1: API key directly
client = LlamaCloud(api_key="your_api_key", base_url="https://api.llamacloud.co")

# Option 2: Environment variable
# export LLAMA_CLOUD_API_KEY="your_api_key"
client = LlamaCloud()
```

### Generating Images

```python
# Generate an image
image = client.generate_image(
    model="glimmer-v1",
    prompt="a beautiful landscape",
    aspect_ratio=LlamaCloud.AspectRatio.LANDSCAPE_16_9,
    image_format=LlamaCloud.ImageFormat.PNG,
    seed=42
)

# Save the image
image.save("landscape")  # Saves as "landscape.png"
```

![A beautiful landscape](assets/landscape.png)
### Generating Videos

```python
# Generate a video
video = client.generate_video(
    model="wan-v1",
    prompt="a flowing river",
    quality=LlamaCloud.VideoQuality.HIGH,
    fps=30
)

# Save the video
video.save("river")  # Saves as "river.mp4"
```

[![Watch the generated video](assets/landscape.png)](assets/river.mp4)
## API Reference

### LlamaCloud

#### `LlamaCloud(api_key=None, base_url="https://api.llamacloud.co", timeout=1200)`

Creates a new client instance.

Parameters:
- `api_key` (Optional[str]): API key for authentication. If not provided, will attempt to use the `LLAMA_CLOUD_API_KEY` environment variable.
- `base_url` (str): Base URL for the API.
- `timeout` (int): Request timeout in seconds. Default is 1200 (20 minutes).

#### `generate_image(model, prompt, aspect_ratio=AspectRatio.SQUARE, image_format=ImageFormat.WEBP, seed=None)`

Generates an image based on the given prompt.

Parameters:
- `model` (str): The model to use for generation.
- `prompt` (str): The prompt describing the image.
- `aspect_ratio` (LlamaCloud.AspectRatio): The aspect ratio of the generated image.
- `image_format` (LlamaCloud.ImageFormat): The format of the generated image.
- `seed` (Optional[int]): Random seed for reproducibility.

Returns:
- `Media`: Media object containing the generated image.

#### `generate_video(model, prompt, quality=LlamaCloud.VideQuality.HIGH, fps=25)`

Generates a video based on the given prompt.

Parameters:
- `model` (str): The model to use for generation.
- `prompt` (str): The prompt describing the video.
- `quality` (LlamaCloud.VideoQuality): The quality of the video (LOW, QUALITY, HIGH).
- `fps` (int): Frames per second of the video.

Returns:
- `Media`: Media object containing the generated video.

### Media

#### `Media(base64_data, format)`

Represents media data (images or videos).

Methods:
- `save(path)`: Saves the media to the specified path. If no extension is provided, the correct one will be added based on the format.

### Exceptions

#### `APIError(status_code, message)`

Raised when the API returns an error.

## License

MIT

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/brilliantai/llamacloud-python.git
cd llamacloud
```

2. Install development dependencies:
```bash
# Using pip
pip install -e . -r dev-requirements.txt

# Using uv (recommended)
uv pip install -e . -r dev-requirements.txt
```

### Running Tests

Run tests with the provided script:
```bash
./scripts/run_tests.sh
```

Or run the commands individually:
```bash
# Run linting
ruff check .

# Run tests with coverage
pytest --cov=llamacloud
```

### CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- Tests are automatically run on all pull requests and pushes to the main branch
- When a new release is created, the package is automatically built and published to PyPI

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please make sure your code passes all tests and linting checks before submitting a pull request.
