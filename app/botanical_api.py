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

"""Public botanical species search API tool using GBIF Global Biodiversity database."""

import os
from urllib.parse import quote

import requests


def search_botanical_species(plant_name: str) -> str:
    """Searches the global GBIF botanical database for scientific taxonomy and plant species info.

    Args:
        plant_name: Common or botanical plant name to query (e.g., 'Monstera', 'Spathiphyllum', 'Snake plant').

    Returns:
        Formatted summary of matching botanical species, family, genus, and scientific taxonomy.
    """
    api_key = os.environ.get("PLANT_API_KEY", "")
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    encoded_query = quote(plant_name.strip())
    url = (
        f"https://api.gbif.org/v1/species/search?q={encoded_query}&rank=SPECIES&limit=5"
    )

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            return (
                f"No botanical species found in GBIF database matching '{plant_name}'."
            )

        species_list = []
        for item in results[:3]:
            scientific_name = item.get("scientificName", "Unknown")
            family = item.get("family", "Unknown")
            genus = item.get("genus", "Unknown")
            status = item.get("taxonomicStatus", "ACCEPTED")
            species_list.append(
                f"- Scientific Name: {scientific_name}\n"
                f"  Family: {family} | Genus: {genus} | Status: {status}"
            )

        return f"Botanical Species Search Results for '{plant_name}':\n" + "\n".join(
            species_list
        )
    except Exception as e:
        return f"Error querying botanical species API for '{plant_name}': {e}"
