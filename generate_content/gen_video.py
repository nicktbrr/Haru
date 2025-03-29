import os
import time
import requests
from lumaai import LumaAI
from dotenv import load_dotenv
import json


def test_video_generation(image_url, prompt):
    """Test video generation using the generated image"""
    print("\nStarting video generation test...")
    client = LumaAI()
    generation = client.generations.create(
        prompt=prompt,
        model="ray-flash-2",
        duration="5s",
        keyframes={"frame0": {"type": "image", "url": image_url}},
    )

    # Poll for completion
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(
                f"Generation failed: {generation.failure_reason}"
            )
        print("Generating video...")
        time.sleep(2)

    print(f"Video generation completed! URL: {generation.assets.video}")
    return generation, generation.assets.video
