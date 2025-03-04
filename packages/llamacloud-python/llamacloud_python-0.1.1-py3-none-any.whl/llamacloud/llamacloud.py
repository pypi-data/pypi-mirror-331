import base64
import os
from enum import Enum
from typing import Optional

import httpx


# Custom exception for API errors
class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"APIError({self.status_code}): {self.message}"

# Media class to handle base64 data and saving
class Media:
    FORMAT_TO_EXT = {
        "WEBP": ".webp",
        "PNG": ".png",
        "JPEG": ".jpg",
        "MP4": ".mp4",
    }

    def __init__(self, base64_data: str, format: str):
        self.base64 = base64_data
        self.format = format

    @property
    def extension(self) -> str:
        """Returns the file extension based on the format."""
        return self.FORMAT_TO_EXT.get(self.format.upper(), "")

    def save(self, path: str) -> None:
        """
        Saves the base64 data to the specified file path.
        If no extension is provided, appends the appropriate one based on format.
        """
        if not os.path.splitext(path)[1]:
            path += self.extension
        with open(path, "wb") as f:
            f.write(base64.b64decode(self.base64))

# LlamaCloud class to interact with the APIs
class LlamaCloud:
    # Nested enum for AspectRatio
    class AspectRatio(str, Enum):
        SQUARE = "1:1"
        LANDSCAPE_16_9 = "16:9"
        LANDSCAPE_21_9 = "21:9"
        LANDSCAPE_3_2 = "3:2"
        PORTRAIT_2_3 = "2:3"
        PORTRAIT_4_5 = "4:5"
        LANDSCAPE_5_4 = "5:4"
        PORTRAIT_3_4 = "3:4"
        LANDSCAPE_4_3 = "4:3"
        PORTRAIT_9_16 = "9:16"
        PORTRAIT_9_21 = "9:21"

    # Nested enum for ImageFormat
    class ImageFormat(str, Enum):
        WEBP = "WEBP"
        PNG = "PNG"
        JPEG = "JPEG"

    # Video Quality Enum
    class VideoQuality(str, Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.llamacloud.co", timeout: int = 60*20):
        """
        Initializes the client with an API key and optional base URL.
        
        If `api_key` is not provided, it will be retrieved from the `LLAMA_CLOUD_API_KEY` environment variable.
        
        Args:
            api_key (Optional[str]): The API key for authentication. If not provided, fetched from the environment.
            base_url (str): The base URL of the API server (default: "https://api.llamacloud.co").
        
        Raises:
            ValueError: If no API key is provided and the environment variable is not set.
        """
        if api_key is None:
            api_key = os.getenv("LLAMA_CLOUD_API_KEY")
            if api_key is None:
                raise ValueError("API key must be provided either as an argument or via the LLAMA_CLOUD_API_KEY environment variable.")
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")

        self.timeout = timeout

    def generate_image(
        self,
        model: str,
        prompt: str,
        aspect_ratio: 'LlamaCloud.AspectRatio' = AspectRatio.SQUARE,
        image_format: 'LlamaCloud.ImageFormat' = ImageFormat.WEBP,
        seed: Optional[int] = None
    ) -> Media:
        """
        Generates an image using the specified parameters.
        
        Args:
            model (str): The model to use for image generation.
            prompt (str): The prompt describing the image.
            aspect_ratio (LlamaCloud.AspectRatio): The aspect ratio (default: SQUARE).
            image_format (LlamaCloud.ImageFormat): The image format (default: WEBP).
            seed (Optional[int]): Random seed for reproducibility (default: None).
        
        Returns:
            Media: An object containing the base64 image data and a save method.
        
        Raises:
            APIError: If the API request fails.
        """
        url = f"{self.base_url}/images/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,  # Serializes to the string value (e.g., "16:9")
            "image_format": image_format,  # Serializes to the string value (e.g., "PNG")
            "seed": seed,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                base64_image = data["image"]
                return Media(base64_image, image_format)
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("detail", "No detail provided")
            except ValueError:
                error_detail = e.response.text
            raise APIError(e.response.status_code, error_detail) from e

    def generate_video(
        self,
        model: str,
        prompt: str,
        quality: 'LlamaCloud.VideoQuality' = VideoQuality.MEDIUM,
        fps: int = 20
    ) -> Media:
        """
        Generates a video using the specified parameters.
        
        Args:
            model (str): The model to use for video generation.
            prompt (str): The prompt describing the video.
            quality (str): The quality level (default: "medium").
            fps (int): Frames per second (default: 20).
        
        Returns:
            Media: An object containing the base64 video data and a save method.
        
        Raises:
            APIError: If the API request fails.
        """
        url = f"{self.base_url}/videos/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "quality": quality,
            "fps": fps,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                base64_video = data["video"]
                return Media(base64_video, "MP4")
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("detail", "No detail provided")
            except ValueError:
                error_detail = e.response.text
            raise APIError(e.response.status_code, error_detail) from e
