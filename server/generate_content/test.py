from google import genai
import os
import time
from dotenv import load_dotenv
from lumaai import LumaAI
import requests
import concurrent.futures
# Import the function from your module
from gen_analysis import generate_music_video_analysis
from gen_image import test_image_generation
from gen_video import video_generation


start_time = time.time()
# Setup
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_KEY"))

# Upload file
myfile = client.files.upload(file='./assets/music/Lofi Girl.mp3')

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

        with open(f'./assets/images/image_{i}.jpg', 'wb') as file:
            file.write(response.content)
        print(f"File downloaded as image_{i}.jpg")
        print(f"Scene {scene.scene_number}: {scene.scene_setting}")
        return (i, image_url)

    # Create a list of tuples containing index and scene data
    scene_data = [(i, scene)
                  for i, scene in enumerate(music_video_scenes.scenes)]

    # Use ThreadPoolExecutor for parallel processing
    image_urls = {}  # Dictionary to store index -> image_url mapping
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks and wait for them to complete
        futures = [executor.submit(generate_and_save_image, data)
                   for data in scene_data]
        # Collect results as they complete
        for future in concurrent.futures.as_completed(futures):
            i, url = future.result()
            image_urls[i] = url

    print("All images generated. Starting video generation...")

    def generate_and_save_video(scene_data):
        i, scene = scene_data
        # Get the corresponding image URL for this scene
        image_url = image_urls[i]
        video_url = video_generation(client, scene.video_prompt, image_url)
        response = requests.get(video_url, stream=True)

        with open(f'./assets/videos/video_{i}.mp4', 'wb') as file:
            file.write(response.content)
        print(f"Video downloaded as video_{i}.mp4")
        print(f"Scene {scene.scene_number}: {scene.scene_setting}")
        return i

    # Use ThreadPoolExecutor for parallel video processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all video generation tasks and wait for them to complete
        futures = [executor.submit(generate_and_save_video, data)
                   for data in scene_data]
        concurrent.futures.wait(futures)

    print("All videos generated successfully!")

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
