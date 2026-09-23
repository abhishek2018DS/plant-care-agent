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

import datetime
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.botanical_api import search_botanical_species
from app.firestore_db import (
    add_or_update_plant,
    get_plant_details,
    list_plants_in_catalog,
)
from app.image_tool import generate_plant_image
from app.maps_tools import find_nearby_places, geocode_address
from app.video_tool import generate_plant_video


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def compute_fertilizer_ratio(
    pot_size_inches: float,
    water_volume_liters: float = 1.0,
    season: str = "growing",
    fertilizer_npk: str = "10-10-10",
) -> str:
    """Computes custom fertilizer concentrate dilution ratios and application guidance.

    Args:
        pot_size_inches: Pot size in inches (e.g., 6.0, 8.0, 10.0).
        water_volume_liters: Volume of water being mixed in liters (default 1.0).
        season: Current season ('growing' for spring/summer, 'dormant' for fall/winter).
        fertilizer_npk: N-P-K formula from fertilizer label (e.g., '10-10-10', '20-20-20').

    Returns:
        Recommended fertilizer concentrate amount in mL and dilution instructions.
    """
    is_dormant = (
        "dormant" in season.lower()
        or "winter" in season.lower()
        or "fall" in season.lower()
    )
    base_ml_per_liter = 2.0
    pot_factor = max(0.5, min(2.0, pot_size_inches / 8.0))

    if is_dormant:
        recommended_ml = base_ml_per_liter * 0.5 * water_volume_liters * pot_factor
        advice = (
            "Dormant season (fall/winter): Apply at half-strength or pause fertilizing."
        )
    else:
        recommended_ml = base_ml_per_liter * water_volume_liters * pot_factor
        advice = "Active growing season (spring/summer): Apply during regular watering every 2-4 weeks."

    return (
        f"Fertilizer Calculation for {pot_size_inches}-inch pot ({fertilizer_npk} formula):\n"
        f"- Mix {recommended_ml:.1f} mL of concentrate into {water_volume_liters} L of water.\n"
        f"- Advice: {advice}"
    )


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a helpful AI assistant designed to provide accurate and useful information. "
        "You remember the user's stated preferences, facts, and specifically ALL user allergies "
        "(such as plant, pollen, food, chemical, or environmental allergies) from previous conversations "
        "and use them to personalize your responses, ensure safety, and avoid recommending or suggesting anything "
        "that conflicts with the user's allergies. Use the plant catalog, fertilizer, botanical species, geocoding, nearby places, and plant image tools to assist users."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(),
    instruction=instruction,
    tools=[
        get_weather,
        get_current_time,
        get_plant_details,
        list_plants_in_catalog,
        add_or_update_plant,
        compute_fertilizer_ratio,
        search_botanical_species,
        geocode_address,
        find_nearby_places,
        generate_plant_image,
        generate_plant_video,
        PreloadMemoryTool(),
        LoadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
