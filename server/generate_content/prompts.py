SONG_DESC_SYSTEM_PROMPT = """
For the artistic style, choose ONE of the following options that best matches the song's mood and tempo:

- Cinematic: Creates dramatic lighting and depth, perfect for a film-like appearance
- 3D Render: Adds realistic textures and depth for a lifelike, digital look

Apply this chosen style consistently across ALL scene prompts.

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

SONG_DESC_USER_PROMPT = """
Create 5 video scenes with matching image prompts that:
- For all scenes generate using Ultra Realistic Graphics.
- IF there are lyrics use the lyrics in the scenes generated.
- When Generating scene images make a smooth transition between each video
- Reflect the song's energy (fast/intense songs get dynamic visuals; slow songs get calmer visuals)
- Maintain ONE consistent artistic style throughout ALL scenes based on the song's mood
- Include the chosen style explicitly in EVERY image prompt
- Feature one main character described in a single sentence"""
