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

from app.firestore_db import (
    PROJECT_ID,
    add_or_update_plant,
    get_plant_details,
    list_plants_in_catalog,
)


def test_project_id_hardcoded():
    """Verify that project ID is hardcoded as expected."""
    assert PROJECT_ID == "qwiklabs-gcp-03-ad649308a5b8"


def test_list_plants_in_catalog():
    """Verify list_plants_in_catalog returns plant items."""
    plants = list_plants_in_catalog()
    assert isinstance(plants, list)
    assert len(plants) >= 4
    plant_names = [p.get("name") for p in plants]
    assert "Monstera Deliciosa" in plant_names


def test_get_plant_details():
    """Verify get_plant_details retrieves specific plant details."""
    details = get_plant_details("Monstera Deliciosa")
    assert details.get("name") == "Monstera Deliciosa"
    assert "watering_schedule" in details


def test_add_or_update_plant():
    """Verify add_or_update_plant creates/updates plant data."""
    result = add_or_update_plant(
        name="Pothos",
        species="Epipremnum aureum",
        watering_schedule="Water every 1-2 weeks",
        light_requirement="Medium indirect light",
        care_instructions="Easy to care for",
        toxicity="Toxic to pets",
        description="Vining houseplant with heart-shaped leaves",
    )
    assert "Pothos" in result
    pothos_details = get_plant_details("Pothos")
    assert pothos_details.get("species") == "Epipremnum aureum"
