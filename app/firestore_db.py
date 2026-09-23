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

"""Firestore backend module for plant-care-agent."""

import logging
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import firestore

# Hardcoded GCP Project ID (do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-03-ad649308a5b8"
COLLECTION_NAME = "plants"

logger = logging.getLogger(__name__)

# Fallback seed data in case Firestore database is not initialized yet in GCP Console
_FALLBACK_PLANTS = {
    "monstera_deliciosa": {
        "id": "monstera_deliciosa",
        "name": "Monstera Deliciosa",
        "species": "Monstera deliciosa",
        "watering_schedule": "Water every 1 to 2 weeks, allowing soil to dry out between waterings.",
        "light_requirement": "Bright to medium indirect light.",
        "care_instructions": "Wipe leaves with a damp cloth to clean dust.",
        "toxicity": "Toxic to cats and dogs if ingested.",
        "description": "Swiss Cheese Plant with iconic split leaves.",
    },
    "snake_plant": {
        "id": "snake_plant",
        "name": "Snake Plant",
        "species": "Dracaena trifasciata",
        "watering_schedule": "Water every 2 to 3 weeks, allowing soil to dry completely between waterings.",
        "light_requirement": "Low to bright indirect light.",
        "care_instructions": "Hardy and low-maintenance. Avoid overwatering.",
        "toxicity": "Mildly toxic to pets.",
        "description": "Upright plant with stiff, sword-like leaves.",
    },
    "peace_lily": {
        "id": "peace_lily",
        "name": "Peace Lily",
        "species": "Spathiphyllum",
        "watering_schedule": "Water weekly or when leaves begin to droop slightly.",
        "light_requirement": "Medium to low indirect light.",
        "care_instructions": "Prefers high humidity.",
        "toxicity": "Toxic to cats and dogs if chewed.",
        "description": "Elegant indoor plant with dark leaves and white spathe flowers.",
    },
    "fiddle_leaf_fig": {
        "id": "fiddle_leaf_fig",
        "name": "Fiddle Leaf Fig",
        "species": "Ficus lyrata",
        "watering_schedule": "Water every 1 to 2 weeks when top 2 inches of soil feel dry.",
        "light_requirement": "Bright, filtered light.",
        "care_instructions": "Avoid drafts or moving the plant frequently.",
        "toxicity": "Toxic to cats and dogs.",
        "description": "Indoor tree with large, violin-shaped leaves.",
    },
}


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client configured with the hardcoded string project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_plants_in_catalog() -> list[dict[str, Any]]:
    """Retrieves all plant documents from the Firestore 'plants' collection.

    Returns:
        A list of plant dictionaries containing plant catalog information.
    """
    try:
        db = get_firestore_client()
        docs = db.collection(COLLECTION_NAME).stream()
        plants = [doc.to_dict() for doc in docs]
        if plants:
            return plants
    except NotFound:
        logger.warning(
            "Firestore database (default) not found. Returning fallback plant catalog."
        )
    except Exception as e:
        logger.warning(
            f"Error querying Firestore: {e}. Returning fallback plant catalog."
        )

    return list(_FALLBACK_PLANTS.values())


def get_plant_details(plant_name: str) -> dict[str, Any]:
    """Look up details for a specific plant by name or ID in the Firestore 'plants' collection.

    Args:
        plant_name: Name or ID of the plant to look up (e.g., 'Monstera Deliciosa', 'snake_plant').

    Returns:
        A dictionary with plant details, watering schedule, light requirement, and care instructions.
    """
    search_key = plant_name.strip().lower().replace(" ", "_")

    try:
        db = get_firestore_client()
        collection_ref = db.collection(COLLECTION_NAME)

        # 1. Direct document ID lookup
        doc_ref = collection_ref.document(search_key)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        # 2. Search by name field match
        docs = collection_ref.stream()
        for d in docs:
            p = d.to_dict()
            if (
                p.get("name", "").lower() == plant_name.strip().lower()
                or search_key in d.id
            ):
                return p
    except NotFound:
        logger.warning("Firestore database (default) not found. Using fallback lookup.")
    except Exception as e:
        logger.warning(f"Error querying Firestore for {plant_name}: {e}")

    # Fallback search
    for key, plant in _FALLBACK_PLANTS.items():
        if plant_name.lower() in plant["name"].lower() or key in search_key:
            return plant

    return {
        "status": "not_found",
        "message": f"No plant found matching '{plant_name}' in the catalog.",
    }


def add_or_update_plant(
    name: str,
    species: str,
    watering_schedule: str,
    light_requirement: str,
    care_instructions: str,
    toxicity: str = "",
    description: str = "",
) -> str:
    """Add a new plant or update an existing plant in the Firestore 'plants' collection.

    Args:
        name: Common name of the plant (e.g., 'Pothos').
        species: Botanical/species name (e.g., 'Epipremnum aureum').
        watering_schedule: How often to water the plant.
        light_requirement: Light conditions needed (e.g., 'Low to bright indirect light').
        care_instructions: Maintenance and care tips.
        toxicity: Information on pet or human toxicity.
        description: General description of the plant.

    Returns:
        Confirmation message string.
    """
    plant_id = name.strip().lower().replace(" ", "_")
    plant_data = {
        "id": plant_id,
        "name": name.strip(),
        "species": species.strip(),
        "watering_schedule": watering_schedule.strip(),
        "light_requirement": light_requirement.strip(),
        "care_instructions": care_instructions.strip(),
        "toxicity": toxicity.strip(),
        "description": description.strip(),
    }

    try:
        db = get_firestore_client()
        doc_ref = db.collection(COLLECTION_NAME).document(plant_id)
        doc_ref.set(plant_data)
        return f"Successfully saved plant '{name}' ({plant_id}) to Firestore collection '{COLLECTION_NAME}'."
    except NotFound:
        _FALLBACK_PLANTS[plant_id] = plant_data
        return f"Saved plant '{name}' ({plant_id}) locally (Firestore database not initialized in GCP)."
    except Exception as e:
        _FALLBACK_PLANTS[plant_id] = plant_data
        return f"Saved plant '{name}' ({plant_id}) locally due to Firestore error: {e}"
