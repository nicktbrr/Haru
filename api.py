import os
import time
import requests
from lumaai import LumaAI
from dotenv import load_dotenv

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
        prompt="A serene Japanese garden with cherry blossoms and a small pond",
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
    return generation.assets.video


def main():
    try:
        # Test image generation
        # image_url = test_image_generation()

        img_url = "https://storage.cdn-luma.com/dream_machine/0e59d73b-95d4-42e1-be6e-7210837bb51c/219e0494-ab6c-48c8-bc6e-e45b7851eac1_result30d9c4f49b3d7d47.jpg"

        # Test video generation using the generated image
        video_url = test_video_generation(img_url)

        print("\nAll tests completed successfully!")
        # print(f"Image URL: {image_url}")
        print(f"Video URL: {video_url}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
