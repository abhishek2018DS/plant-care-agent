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

"""Video generation tool using gemini-omni-flash-preview in global region."""

import base64
import time

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types as genai_types

BUCKET_NAME = "plant-care-agent-media-8a5b8"
PROJECT_ID = "qwiklabs-gcp-03-ad649308a5b8"


async def generate_plant_video(
    prompt: str,
    tool_context: ToolContext,
    filename: str = "generated_plant_video.mp4",
) -> str:
    """Generates a short video for a plant care item using Google's Omni model (gemini-omni-flash-preview) in the global region.
    Saves the video as an artifact with tool_context.save_artifact and uploads it to the public Cloud Storage bucket.

    Args:
        prompt: Description of the plant video to generate (e.g. 'A short video showing a Monstera plant being watered').
        tool_context: ADK ToolContext provided automatically by the agent framework.
        filename: Name for the saved video file and artifact (default 'generated_plant_video.mp4').

    Returns:
        Public HTTPS URL of the generated video uploaded to Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        # 1. Initialize GenAI client in global region for gemini-omni-flash-preview
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if hasattr(interaction, "steps") and interaction.steps:
            for step in interaction.steps:
                content_list = (
                    getattr(step, "content", None)
                    or getattr(step, "contents", None)
                    or []
                )
                for item in content_list:
                    item_type = getattr(item, "type", None) or ""
                    item_mime = getattr(item, "mime_type", None) or ""
                    if (
                        item_type == "video"
                        or item_mime.startswith("video/")
                        or "video" in str(item_type).lower()
                    ):
                        data = getattr(item, "data", None)
                        if data:
                            if isinstance(data, str):
                                video_bytes = base64.b64decode(data)
                            elif isinstance(data, bytes):
                                video_bytes = data
                            if item_mime:
                                mime_type = item_mime
                            break
                        uri = getattr(item, "uri", None)
                        if uri:
                            import requests

                            res = requests.get(uri)
                            if res.status_code == 200:
                                video_bytes = res.content
                                if item_mime:
                                    mime_type = item_mime
                            break

        if not video_bytes:
            # Fallback if bytes were not extracted directly from step content
            return f"Error: Failed to retrieve video bytes for prompt: '{prompt}' using gemini-omni-flash-preview."

        # Ensure filename has a video extension
        if not (filename.endswith(".mp4") or filename.endswith(".webm")):
            filename = f"{filename}.mp4"

        # Unique object name to avoid overwriting
        object_name = f"plant_videos/{int(time.time())}_{filename}"

        # 2. Save artifact using tool_context.save_artifact so it shows up in Playground's Artifacts panel
        artifact_part = genai_types.Part.from_bytes(
            data=video_bytes,
            mime_type=mime_type,
        )
        if tool_context and hasattr(tool_context, "save_artifact"):
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
            )

        # 3. Upload video bytes directly to public GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return public_url

    except Exception as e:
        return f"Error generating or uploading plant video: {e}"
