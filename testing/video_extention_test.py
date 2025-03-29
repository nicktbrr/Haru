import requests
import time
import os

from lumaai import LumaAI
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

print(os.environ.get("LUMAAI_API_KEY"))

client = LumaAI()

# generation_orig = client.generations.create(
#     prompt="A forest in winter with snow falling and elk running around the clearing",
# )
# completed = False
# while not completed:
#     generation = client.generations.get(id=generation_orig.id)
#     if generation.state == "completed":
#         completed = True
#     elif generation.state == "failed":
#         raise RuntimeError(f"Generation failed: {generation.failure_reason}")
#     print("Dreaming")
#     time.sleep(3)

# video_url = generation.assets.video
# print(video_url)

# print(generation_orig.id)

generation = client.generations.create(
    prompt="A pack wolfs coming out of the trees from the right of screen chasing the elk away.",
    keyframes={
        "frame0": {
            "type": "generation",
            "id": "12fb0292-62cb-4d39-96ee-ffd05a607f87",
        }
    },
    model="ray-2",
    duration="9s"
)

completed = False
while not completed:
    generation = client.generations.get(id=generation.id)
    if generation.state == "completed":
        completed = True
    elif generation.state == "failed":
        raise RuntimeError(f"Generation failed: {generation.failure_reason}")
    print("Dreaming")
    time.sleep(3)

video_url = generation.assets.video
print(video_url)

print(generation.id)
