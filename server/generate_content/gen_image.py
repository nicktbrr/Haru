import time


def test_image_generation(client, prompt, aspect_ratio="9:16"):
    """Test image generation and return the image URL"""
    print("Starting image generation test...")

    # Create an image generation
    generation = client.generations.image.create(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
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
