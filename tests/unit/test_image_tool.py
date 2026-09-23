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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent import root_agent
from app.image_tool import BUCKET_NAME, generate_plant_image


def test_image_tool_registered_on_agent():
    """Verify generate_plant_image is registered as a tool on root_agent."""
    assert generate_plant_image in root_agent.tools


@pytest.mark.asyncio
async def test_generate_plant_image_success():
    """Test generate_plant_image saves artifact and uploads bytes to GCS bucket."""
    mock_bytes = b"\xff\xd8\xff\xe0mock_image_data"

    # Mock Candidate & Part
    mock_part = MagicMock()
    mock_part.inline_data.data = mock_bytes
    mock_part.inline_data.mime_type = "image/jpeg"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    # Mock GenAI client
    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    # Mock storage client
    mock_storage_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Mock tool_context
    mock_tool_context = AsyncMock()

    with (
        patch("app.image_tool.genai.Client", return_value=mock_genai_client),
        patch("app.image_tool.storage.Client", return_value=mock_storage_client),
    ):
        result_url = await generate_plant_image(
            prompt="A Monstera plant",
            tool_context=mock_tool_context,
            filename="monstera.jpg",
        )

        assert result_url.startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/")
        assert "monstera.jpg" in result_url

        # Verify save_artifact was called
        mock_tool_context.save_artifact.assert_called_once()

        # Verify upload_from_string was called with image bytes
        mock_blob.upload_from_string.assert_called_once_with(
            mock_bytes, content_type="image/jpeg"
        )
