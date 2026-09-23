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
from app.maps_tools import find_nearby_places, geocode_address


def test_maps_tools_registered_on_agent():
    """Verify geocode_address and find_nearby_places are registered on root_agent."""
    assert geocode_address in root_agent.tools
    assert find_nearby_places in root_agent.tools


def test_geocode_address_missing_key(monkeypatch):
    """Test geocode_address error message when API key is missing or placeholder."""
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "PASTE_KEY_HERE")
    result = geocode_address("1600 Amphitheatre Pkwy, Mountain View, CA")
    assert "GOOGLE_MAPS_API_KEY" in result


def test_find_nearby_places_missing_key(monkeypatch):
    """Test find_nearby_places error message when API key is missing or placeholder."""
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "")
    result = find_nearby_places(37.422, -122.084, "florist")
    assert "GOOGLE_MAPS_API_KEY" in result
