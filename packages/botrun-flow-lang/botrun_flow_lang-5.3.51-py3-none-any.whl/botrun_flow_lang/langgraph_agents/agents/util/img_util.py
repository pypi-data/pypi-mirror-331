import anthropic
import base64
import httpx
import mimetypes
import os
import imghdr
from pathlib import Path


def get_img_content_type(file_path: str | Path) -> str:
    """
    Get the content type (MIME type) of a local file.
    This function checks the actual image format rather than relying on file extension.

    Args:
        file_path: Path to the local file (can be string or Path object)

    Returns:
        str: The content type of the file (e.g., 'image/jpeg', 'image/png')

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file type is not recognized or not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check actual image type using imghdr
    img_type = imghdr.what(file_path)
    if not img_type:
        raise ValueError(f"File is not a recognized image format: {file_path}")

    # Map image type to MIME type
    mime_types = {
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }

    content_type = mime_types.get(img_type.lower())
    if not content_type:
        raise ValueError(f"Unsupported image format '{img_type}': {file_path}")

    return content_type


def analyze_imgs(img_urls: list[str], user_input: str) -> str:
    """
    Analyze multiple images using Claude Vision API

    Args:
        img_urls: List of URLs to the image files
        user_input: User's query about the image content(s)

    Returns:
        str: Claude's analysis of the image content(s) based on the query
    """
    try:
        # Initialize message content
        message_content = []

        # Download and encode each image file from URLs
        with httpx.Client(follow_redirects=True) as client:
            for img_url in img_urls:
                response = client.get(img_url)
                if response.status_code != 200:
                    return f"Error: Failed to download image from URL: {img_url}"

                # Detect content type from response headers
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return f"Error: URL does not point to a valid image: {img_url}"

                # Check file size (5MB limit for API)
                if len(response.content) > 5 * 1024 * 1024:
                    return f"Error: Image file size exceeds 5MB limit: {img_url}"

                # Encode image data
                img_data = base64.standard_b64encode(response.content).decode("utf-8")

                # Add image to message content
                message_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_type,
                            "data": img_data,
                        },
                    }
                )

            # Add user input text
            message_content.append({"type": "text", "text": user_input})

            # Initialize Anthropic client
            client = anthropic.Anthropic()

            # Send to Claude
            message = client.messages.create(
                model="claude-3-7-sonnet-latest",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ],
            )

            return message.content[0].text

    except httpx.RequestError as e:
        return f"Error: Failed to download image(s): {str(e)}"
    except anthropic.APIError as e:
        return f"Error accessing Claude API: {str(e)}"
    except Exception as e:
        return f"Error analyzing image(s): {str(e)}"
