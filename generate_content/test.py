from google import genai
import os
from dotenv import load_dotenv
from lumaai import LumaAI
import requests
import concurrent.futures
# Import the function from your module
from gen_analysis import generate_music_video_analysis
from gen_image import test_image_generation

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

    client = LumaAI()

    def generate_and_save_image(scene_data):
        i, scene = scene_data
        image_url = test_image_generation(client, scene.image_prompt)
        response = requests.get(image_url, stream=True)

        with open(f'image_{i}.jpg', 'wb') as file:
            file.write(response.content)
        print(f"File downloaded as image_{i}.jpg")
        print(f"Scene {scene.scene_number}: {scene.scene_setting}")
        return i

    # Create a list of tuples containing index and scene data
    scene_data = [(i, scene)
                  for i, scene in enumerate(music_video_scenes.scenes)]

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks and wait for them to complete
        futures = [executor.submit(generate_and_save_image, data)
                   for data in scene_data]
        concurrent.futures.wait(futures)
