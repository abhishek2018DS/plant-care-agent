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

"""Seed script to populate Firestore 'plants' collection."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-ad649308a5b8"
COLLECTION_NAME = "plants"

SEED_PLANTS = [
    {
        "id": "monstera_deliciosa",
        "name": "Monstera Deliciosa",
        "species": "Monstera deliciosa",
        "watering_schedule": "Water every 1 to 2 weeks, allowing soil to dry out between waterings. Water more frequently in brighter light and less in lower light.",
        "light_requirement": "Bright to medium indirect light. Avoid direct sunlight as it may burn the leaves.",
        "care_instructions": "Wipe leaves periodically with a damp cloth to clean dust. Provide a moss pole or trellis for support as it grows.",
        "toxicity": "Toxic to cats and dogs if ingested.",
        "description": "Known as the Swiss Cheese Plant, iconic for its dramatic split leaves and lush tropical foliage.",
    },
    {
        "id": "snake_plant",
        "name": "Snake Plant",
        "species": "Dracaena trifasciata",
        "watering_schedule": "Water every 2 to 3 weeks, allowing soil to dry completely between waterings. Reduce watering in winter.",
        "light_requirement": "Low to bright indirect light. Very tolerant of low light conditions.",
        "care_instructions": "Hardy and low-maintenance. Avoid overwatering to prevent root rot.",
        "toxicity": "Mildly toxic to pets.",
        "description": "An upright, structural indoor plant with stiff, sword-like leaves.",
    },
    {
        "id": "peace_lily",
        "name": "Peace Lily",
        "species": "Spathiphyllum",
        "watering_schedule": "Water weekly or when leaves begin to droop slightly. Keep soil consistently moist but not soggy.",
        "light_requirement": "Medium to low indirect light. Thrives under fluorescent office lighting.",
        "care_instructions": "Prefers high humidity. Mist leaves occasionally or place near a humidifier.",
        "toxicity": "Toxic to cats and dogs if chewed.",
        "description": "Elegant indoor plant with glossy dark leaves and white spathe flowers.",
    },
    {
        "id": "fiddle_leaf_fig",
        "name": "Fiddle Leaf Fig",
        "species": "Ficus lyrata",
        "watering_schedule": "Water every 1 to 2 weeks when the top 2 inches of soil feel dry.",
        "light_requirement": "Bright, filtered light. Needs several hours of indirect sunlight daily.",
        "care_instructions": "Avoid moving the plant around. Keep away from drafts or cold air vents.",
        "toxicity": "Toxic to cats and dogs.",
        "description": "Dramatic indoor tree with large, violin-shaped leaves.",
    },
]


def seed_database() -> None:
    """Seed the Firestore database with indoor plant items."""
    db = firestore.Client(project=PROJECT_ID)
    plants_ref = db.collection(COLLECTION_NAME)
    print(
        f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'..."
    )
    for plant in SEED_PLANTS:
        doc_ref = plants_ref.document(plant["id"])
        doc_ref.set(plant)
        print(f"  - Seeded plant: {plant['name']} ({plant['id']})")
    print("Seeding complete!")


if __name__ == "__main__":
    seed_database()
