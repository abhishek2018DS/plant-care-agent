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

import pytest
from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.agent import generate_memories_callback, root_agent


def test_agent_memory_configuration():
    """Verify root_agent includes memory tools, callbacks, and allergy instructions."""
    # Check tools
    tool_types = [type(t) for t in root_agent.tools]
    assert PreloadMemoryTool in tool_types, (
        "PreloadMemoryTool must be included in root_agent tools"
    )
    assert LoadMemoryTool in tool_types, (
        "LoadMemoryTool must be included in root_agent tools"
    )

    # Check callback
    assert root_agent.after_agent_callback == generate_memories_callback, (
        "after_agent_callback must be set to generate_memories_callback"
    )

    # Check instruction
    assert "allergies" in root_agent.instruction.lower(), (
        "Agent instruction must mention user allergies"
    )


@pytest.mark.asyncio
async def test_generate_memories_callback():
    """Test generate_memories_callback invokes add_session_to_memory."""

    class DummyContext:
        def __init__(self):
            self.called = False

        async def add_session_to_memory(self):
            self.called = True

    ctx = DummyContext()
    await generate_memories_callback(ctx)
    assert ctx.called, (
        "generate_memories_callback must call add_session_to_memory on context"
    )
