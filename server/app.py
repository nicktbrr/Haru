from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from werkzeug.utils import secure_filename
import json
from google import genai
import requests
from lumaai import LumaAI
import concurrent.futures
from generate_content.gen_analysis import generate_music_video_analysis
from generate_content.gen_image import test_image_generation
from generate_content.gen_video import video_generation
from utils.stitch_videos import merge_videos_with_audio
from dotenv import load_dotenv
import shutil

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure upload settings
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."
)
app.config["MUSIC_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "music"
)
app.config["VIDEO_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "videos"
)
app.config["SESSIONS_FILE"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "sessions.json"
)

app.config["OUTPUT_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "output"
)

# Configure Next.js public directory
app.config["NEXT_PUBLIC_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "client", "public", "assets", "output"
)

# Create necessary folders
os.makedirs(app.config["MUSIC_FOLDER"], exist_ok=True)
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
os.makedirs(app.config["NEXT_PUBLIC_FOLDER"], exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_music():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Check file extension
    allowed_extensions = {".mp3", ".wav"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return (
            jsonify(
                {
                    "error": "Invalid file type. Only MP3 and WAV files are allowed."
                }
            ),
            400,
        )

    if file:
        try:
            # Generate a unique session ID
            session_id = str(time.time())

            unique_filename = f"{session_id}{file_ext}"
            filepath = os.path.join(app.config["MUSIC_FOLDER"], unique_filename)
            file.save(filepath)

            return jsonify(
                {
                    "message": "File uploaded successfully",
                }
            )
        except Exception as e:
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500


@app.route("/generate", methods=["POST"])
def generate_video():
    try:
        # Get all files in the music directory
        music_files = os.listdir(app.config["MUSIC_FOLDER"])

        if not music_files:
            return (
                jsonify(
                    {
                        "error": "No music files found in the assets/music directory"
                    }
                ),
                400,
            )

        # Get the video format and adjustment parameters from the request
        data = request.get_json()
        video_format = data.get("format", "youtube")
        brightness = data.get("brightness", 50)
        contrast = data.get("contrast", 50)
        print(f"Received video format from frontend: {video_format}")
        print(f"Received brightness: {brightness}, contrast: {contrast}")

        # Map video format to aspect ratio
        aspect_ratio_map = {
            "youtube": "16:9",
            "horizontal": "4:3",
            "vertical": "9:16",
        }
        aspect_ratio = aspect_ratio_map.get(video_format, "16:9")
        print(f"Mapped to aspect ratio: {aspect_ratio}")

        # Get the most recent file based on modification time
        latest_file = max(
            music_files,
            key=lambda x: os.path.getmtime(
                os.path.join(app.config["MUSIC_FOLDER"], x)
            ),
        )

        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            audio_file_path = os.path.join(
                app.config["MUSIC_FOLDER"], latest_file
            )
            music_video_scenes = generate_music_video_analysis(
                audio_file_path, client
            )
            print(music_video_scenes)
        except Exception as e:
            print(f"Error generating music video scenes: {str(e)}")
            return (
                jsonify(
                    {"error": f"Error generating music video scenes: {str(e)}"}
                ),
                500,
            )

        print(music_video_scenes)

        # Generate video
        client = LumaAI()

        def generate_and_save_image(scene_data):
            i, scene = scene_data
            image_url = test_image_generation(
                client, scene.image_prompt, aspect_ratio
            )
            response = requests.get(image_url, stream=True)

            with open(f"./assets/images/image_{i}.jpg", "wb") as file:
                file.write(response.content)
            print(f"File downloaded as image_{i}.jpg")
            return (i, image_url)

        # Create a list of tuples containing index and scene data
        scene_data = [
            (i, scene) for i, scene in enumerate(music_video_scenes.scenes)
        ]

        # Use ThreadPoolExecutor for parallel processing
        image_urls = {}  # Dictionary to store index -> image_url mapping
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks and wait for them to complete
            futures = [
                executor.submit(generate_and_save_image, data)
                for data in scene_data
            ]
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                i, url = future.result()
                image_urls[i] = url

        print("All images generated. Starting video generation...")

        def generate_and_save_video(scene_data):
            i, scene = scene_data
            # Get the corresponding image URL for this scene
            image_url = image_urls[i]
            try:
                video_url = video_generation(
                    client, scene.video_prompt, image_url, aspect_ratio
                )
                response = requests.get(video_url, stream=True)

                with open(f"./assets/videos/video_{i}.mp4", "wb") as file:
                    file.write(response.content)
                print(f"Video downloaded as video_{i}.mp4")
                return video_url
            except Exception as e:
                print(f"Error generating video for scene {i}: {str(e)}")
                raise

        # Use ThreadPoolExecutor for parallel video processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all video generation tasks and wait for them to complete
            futures = [
                executor.submit(generate_and_save_video, data)
                for data in scene_data
            ]
            try:
                concurrent.futures.wait(futures)
            except Exception as e:
                print(f"Error in video generation: {str(e)}")
                return (
                    jsonify({"error": f"Error generating videos: {str(e)}"}),
                    500,
                )

        print("All videos generated successfully!")

        # Create proper output path with filename
        output_file = os.path.join(app.config["OUTPUT_FOLDER"], "output.mp4")
        audio_file_path = os.path.join(app.config["MUSIC_FOLDER"], latest_file)

        success = merge_videos_with_audio(
            video_dir=app.config["VIDEO_FOLDER"],
            output_path=output_file,
            audio_file=audio_file_path,
            normalize=True,
            brightness=brightness,
            contrast=contrast,
        )

        if not success:
            return jsonify({"error": "Failed to merge videos"}), 500

        # Copy the video to the Next.js public directory
        public_output_file = os.path.join(
            app.config["NEXT_PUBLIC_FOLDER"], "output.mp4"
        )
        shutil.copy2(output_file, public_output_file)

        return jsonify(
            {
                "message": "Found latest music file",
                "filename": latest_file,
                "filepath": audio_file_path,
                "output_file": output_file,
                "videoUrl": "/assets/output/output.mp4",
            }
        )

    except Exception as e:
        print(f"Error in generate_video: {str(e)}")
        return jsonify({"error": f"Error finding music file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
