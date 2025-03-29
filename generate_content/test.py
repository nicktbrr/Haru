from google import genai
import os
from dotenv import load_dotenv

# Import the function from your module
from gen_analysis import generate_music_video_analysis

# Setup
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_KEY"))

# Upload file
myfile = client.files.upload(file='./Lofi Girl.mp3')

# Generate analysis
music_video_scenes = generate_music_video_analysis(myfile, client)

# Use the returned object
if music_video_scenes:
    # The classes are already imported through your function
    print(f"Analysis complete for: {music_video_scenes.song_analysis.title}")

    # Access any properties
    for scene in music_video_scenes.scenes:
        print(f"Scene {scene.scene_number}: {scene.scene_setting}")
