import time


def video_generation(client, prompt, image_url, aspect_ratio="9:16"):
    """Generate video using the provided image and aspect ratio"""
    print(f"\nStarting video generation with aspect ratio: {aspect_ratio}")

    generation = client.generations.create(
        prompt=prompt,
        model="ray-flash-2",
        duration="5s",
        aspect_ratio=aspect_ratio,
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
        print(f"Generating video with aspect ratio {aspect_ratio}...")
        time.sleep(2)

    print(f"Video generation completed! URL: {generation.assets.video}")
    return generation.assets.video
