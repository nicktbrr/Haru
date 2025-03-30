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
from generate_content.gen_video import test_video_generation


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

# Create necessary folders
os.makedirs(app.config["MUSIC_FOLDER"], exist_ok=True)
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)


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
                404,
            )

        # Get the most recent file based on modification time
        latest_file = max(
            music_files,
            key=lambda x: os.path.getmtime(
                os.path.join(app.config["MUSIC_FOLDER"], x)
            ),
        )

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        music_video_scenes = generate_music_video_analysis(latest_file, client)
        # description = "A Jet flying over the city"

        # Generate video
        # video_url = luma_connector.generate_video(prompt=description)
        client = LumaAI()

        def generate_and_save_image(scene_data):
            i, scene = scene_data
            image_url = test_image_generation(client, scene.image_prompt)
            response = requests.get(image_url, stream=True)

            with open(f"image_{i}.jpg", "wb") as file:
                file.write(response.content)
            print(f"File downloaded as image_{i}.jpg")
            print(f"Scene {scene.scene_number}: {scene.scene_setting}")
            return image_url

        # Create a list of tuples containing index and scene data
        scene_data = [
            (i, scene) for i, scene in enumerate(music_video_scenes.scenes)
        ]

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks and wait for them to complete
            futures = [
                executor.submit(generate_and_save_image, data)
                for data in scene_data
            ]
            image_urls = [future.result() for future in futures]
                    # Generate videos for all scenes
            video_urls = []
            video_filenames = []
            timestamp = int(
                time.time()
            )  # Use same timestamp for the batch but unique scene numbers

            for i, (image_url, scene) in enumerate(
                zip(image_urls, music_video_scenes.scenes)
            ):
                try:
                    generation, video_url = test_video_generation(
                        image_url, scene.scene_setting
                    )
                    video_urls.append(video_url)

                    # Create unique filename for each video using scene number
                    video_filename = (
                        f"video_{timestamp}_scene_{scene.scene_number}.mp4"
                    )
                    video_filenames.append(video_filename)
                    video_path = os.path.join(
                        app.config["VIDEO_FOLDER"], video_filename
                    )

                    print(
                        f"Downloading video for scene {scene.scene_number} from {video_url}"
                    )
                    response = requests.get(video_url)
                    if response.status_code == 200:
                        with open(video_path, "wb") as f:
                            f.write(response.content)
                        print(f"Successfully saved video to {video_path}")
                    else:
                        print(
                            f"Failed to download video: Status code {response.status_code}"
                        )
                        raise Exception(
                            f"Failed to download video for scene {scene.scene_number}"
                        )
                except Exception as e:
                    print(
                        f"Error processing scene {scene.scene_number}: {str(e)}"
                    )
                    raise

        return jsonify(
            {
                "message": "Found latest music file",
                "filename": latest_file,
                "filepath": os.path.join(
                    app.config["MUSIC_FOLDER"], latest_file
                ),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error finding music file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
