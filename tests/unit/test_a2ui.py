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

from unittest.mock import MagicMock

from google.adk.models.llm_response import LlmResponse
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.agent import root_agent


def test_root_agent_has_a2ui_callback():
    """Verify root_agent has after_model_callback set to a2ui_callback."""
    assert root_agent.after_model_callback == a2ui_callback


def test_a2ui_callback_transforms_a2ui_json():
    """Verify a2ui_callback transforms raw A2UI JSON response into wrapped Blob format."""
    raw_a2ui_json = """[
        {
            "beginRendering": {
                "surfaceId": "surface-1",
                "root": "card-1"
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "surface-1",
                "components": [
                    {
                        "id": "card-1",
                        "component": {
                            "Card": {
                                "child": "text-1"
                            }
                        }
                    },
                    {
                        "id": "text-1",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Hello Plant Lover!"},
                                "usageHint": "body"
                            }
                        }
                    }
                ]
            }
        }
    ]"""

    llm_response = LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=raw_a2ui_json)],
        )
    )

    mock_context = MagicMock()
    result = a2ui_callback(mock_context, llm_response)

    assert result is not None
    assert result.custom_metadata == {"a2a:response": "true"}
    assert len(result.content.parts) == 2
    blob = result.content.parts[0].inline_data
    assert blob is not None
    assert blob.data is not None
    assert b"<a2a_datapart_json>" in blob.data
    assert b"beginRendering" in blob.data
