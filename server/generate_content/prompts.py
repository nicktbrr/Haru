SONG_DESC_SYSTEM_PROMPT = """
Format response as this JSON:
{
  "song_analysis": {
    "genre": "",
    "tempo_bpm": "",
    "mood": "",
    "lyrical_themes": "",
    "instrumentation": "",
    "artistic_style": "",
    "character_description": ""
  },
  "scenes": [
    {
      "scene_number": 1,
      "video_prompt": "",
      "image_prompt": ""
    },
    // Continue for 5 scenes total
  ]
}"""

SONG_DESC_USER_PROMPT = f"""
Create 5 video scenes with matching image prompts that:
- Reflect the song's energy (fast/intense songs get dynamic visuals; slow songs get calmer visuals)
- Maintain ONE consistent artistic style throughout ALL scenes based on the song's mood
- Include the chosen style explicitly in EVERY image prompt
- Feature one main character described in a single sentence"""
