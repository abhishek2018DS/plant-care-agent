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

from app.agent import root_agent
from app.botanical_api import search_botanical_species


def test_search_botanical_species_real_data():
    """Test search_botanical_species calls GBIF API and returns real taxonomy data."""
    result = search_botanical_species("Monstera deliciosa")
    assert "Monstera deliciosa" in result or "Araceae" in result
    assert "Scientific Name:" in result or "Family:" in result


def test_botanical_tool_registered_on_agent():
    """Verify search_botanical_species is registered on root_agent."""
    assert search_botanical_species in root_agent.tools
