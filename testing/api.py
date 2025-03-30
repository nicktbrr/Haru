import os
import time
import requests
from lumaai import LumaAI
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()

print(os.environ.get("LUMAAI_API_KEY"))

# Initialize the client with API key
client = LumaAI()


def test_image_generation():
    """Test image generation and return the image URL"""
    print("Starting image generation test...")

    # Create an image generation
    generation = client.generations.image.create(
        prompt="A serene Japanese garden with cherry blossoms and a small pond make it realistic and put swans in the pond",
        aspect_ratio="16:9",
        model="photon-1"
    )

    # Poll for completion
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(
                f"Generation failed: {generation.failure_reason}")
        print("Generating image...")
        time.sleep(2)

    print(f"Image generation completed! URL: {generation.assets.image}")
    return generation.assets.image


def test_video_generation(image_url):
    """Test video generation using the generated image"""
    print("\nStarting video generation test...")

    generation = client.generations.create(
        prompt="Swams coming into the scenes then swimming under the bridge, making teh water have physics and some wind with some leaves blowing.",
        keyframes={
            "frame0": {
                "type": "image",
                "url": image_url
            }
        }
    )

    # Poll for completion
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(
                f"Generation failed: {generation.failure_reason}")
        print("Generating video...")
        time.sleep(2)

    print(f"Video generation completed! URL: {generation.assets.video}")
    print(generation)
    with open("generation.json", "w") as f:
        json.dump(generation, f)
    return generation.assets.video


def main():
    try:
        # Test image generation
        image_url = test_image_generation()

        # Test video generation using the generated image
        video_url = test_video_generation(image_url)

        print("\nAll tests completed successfully!")
        print(f"Image URL: {image_url}")
        print(f"Video URL: {video_url}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
