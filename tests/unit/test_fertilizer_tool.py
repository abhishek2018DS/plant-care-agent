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

from app.agent import compute_fertilizer_ratio, root_agent


def test_compute_fertilizer_ratio_growing_season():
    """Test compute_fertilizer_ratio calculation for growing season."""
    result = compute_fertilizer_ratio(
        pot_size_inches=8.0,
        water_volume_liters=1.0,
        season="growing",
        fertilizer_npk="10-10-10",
    )
    assert "2.0 mL" in result
    assert "Active growing season" in result


def test_compute_fertilizer_ratio_dormant_season():
    """Test compute_fertilizer_ratio calculation for dormant season."""
    result = compute_fertilizer_ratio(
        pot_size_inches=8.0,
        water_volume_liters=1.0,
        season="dormant",
        fertilizer_npk="10-10-10",
    )
    assert "1.0 mL" in result
    assert "Dormant season" in result


def test_tool_registered_on_agent():
    """Verify compute_fertilizer_ratio is registered as a tool on root_agent."""
    assert compute_fertilizer_ratio in root_agent.tools
