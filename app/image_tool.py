# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Image generation tool using gemini-3.1-flash-lite-image in global region."""

import time

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types as genai_types

BUCKET_NAME = "plant-care-agent-media-8a5b8"
PROJECT_ID = "qwiklabs-gcp-03-ad649308a5b8"


async def generate_plant_image(
    prompt: str,
    tool_context: ToolContext,
    filename: str = "generated_plant.jpg",
) -> str:
    """Generates an image for a plant item using gemini-3.1-flash-lite-image, saves it as an artifact, and uploads it to Cloud Storage.

    Args:
        prompt: Description of the plant image to generate (e.g. 'A lush green Monstera Deliciosa in a ceramic pot').
        tool_context: ADK ToolContext provided automatically by the agent framework.
        filename: Name for the saved image file and artifact (default 'generated_plant.jpg').

    Returns:
        Public HTTPS URL of the generated image uploaded to Cloud Storage.
    """
    try:
        # 1. Initialize GenAI client in global region for gemini-3.1-flash-lite-image
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data and part.inline_data.data:
                            image_bytes = part.inline_data.data
                            mime_type = part.inline_data.mime_type or "image/jpeg"
                            break

        if not image_bytes:
            return f"Error: Failed to generate image bytes for prompt: '{prompt}'."

        # Ensure filename has an image extension
        if not (
            filename.endswith(".jpg")
            or filename.endswith(".png")
            or filename.endswith(".jpeg")
        ):
            filename = f"{filename}.jpg"

        # Unique object name to avoid overwriting
        object_name = f"plant_images/{int(time.time())}_{filename}"

        # 2. Save artifact using tool_context
        artifact_part = genai_types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )
        if tool_context and hasattr(tool_context, "save_artifact"):
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
            )

        # 3. Upload image bytes directly to public GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return public_url

    except Exception as e:
        return f"Error generating or uploading plant image: {e}"
