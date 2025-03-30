from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import re
import json
from pydantic import ValidationError
from .prompts import SONG_DESC_SYSTEM_PROMPT, SONG_DESC_USER_PROMPT


class SongAnalysis(BaseModel):
    genre: str
    tempo_bpm: str = Field(..., description="Approximate BPM")
    mood: str
    lyrical_themes: str
    instrumentation: str
    artistic_style: str
    character_description: str = Field(...,
                                       description="Brief character description (max 3 sentences)")


class Scene(BaseModel):
    scene_number: int
    video_prompt: str
    image_prompt: str


class MusicVideoScenes(BaseModel):
    song_analysis: SongAnalysis
    scenes: List[Scene]


def generate_music_video_analysis(song_path: str, client, song_title=None, song_artist=None, ) -> MusicVideoScenes:

    system_instructions = SONG_DESC_SYSTEM_PROMPT
    user_prompt = SONG_DESC_USER_PROMPT

    print("song_path", song_path)

    myfile = client.files.upload(file=song_path)

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        config=types.GenerateContentConfig(
            system_instruction=system_instructions),
        contents=[user_prompt, myfile]
    )

    json_str = response.text

    try:
        # Check if the response contains markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```',
                               response.text, re.DOTALL)

        if json_match:
            # Extract just the JSON without the markdown code block tags
            json_str = json_match.group(1)
        else:
            # If no markdown code blocks, use the full response
            json_str = response.text

        # Parse the JSON string
        music_video_data = json.loads(json_str)

        # Create a MusicVideoScenes instance
        music_video_scenes = MusicVideoScenes(**music_video_data)

        print("Successfully parsed response into MusicVideoScenes object!")
        print(f"Number of scenes: {len(music_video_scenes.scenes)}")

        # You can also save the entire structured data
        with open('music_video_storyboard.json', 'w') as f:
            json.dump(music_video_data, f, indent=2)
        return music_video_scenes

    except json.JSONDecodeError as e:
        print("Error parsing JSON response:", e)
        print("Raw response:", response.text)
        return None
    except ValidationError as e:
        print("Pydantic validation error:", e)
        print("JSON data received:", music_video_data)
        return None
    except Exception as e:
        print("Error creating MusicVideoScenes object:", e)
        print("Exception:", str(e))
        return None
