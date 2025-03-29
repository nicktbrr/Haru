from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
import os
from google import genai
from werkzeug.utils import secure_filename
from gemini_connector import (
    GeminiMusicAnalyzer,
    LumaAIConnector,
    generate_video,
)
from generate_content.gen_analysis import generate_music_video_analysis
from generate_content.gen_image import test_image_generation
from generate_content.gen_video import test_video_generation
import tempfile
import requests
from urllib.parse import urlparse
import time
from lumaai import LumaAI
import concurrent.futures

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
app.config["VIDEO_FOLDER"] = os.path.join(app.config["UPLOAD_FOLDER"], "videos")

# Create video folder if it doesn't exist
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

# Initialize the analyzers
# gemini_analyzer = GeminiMusicAnalyzer()
luma_connector = LumaAIConnector()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join("music", filename)
        file.save(filepath)

        try:
            # Get music description
            # description = gemini_analyzer.describe_music(filepath)
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            music_video_scenes = generate_music_video_analysis(filepath, client)
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
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=5
            ) as executor:
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

            # Clean up the audio file
            os.remove(filepath)

            # Create response with scene information
            scene_data = []
            for scene, video_filename in zip(
                music_video_scenes.scenes, video_filenames
            ):
                scene_data.append(
                    {
                        "scene_number": scene.scene_number,
                        "scene_setting": scene.scene_setting,
                        "video_url": f"/video/{video_filename}",
                        "download_url": f"/download/{video_filename}",
                    }
                )

            print(f"Returning scene data: {scene_data}")  # Debug print
            return jsonify({"scenes": scene_data})

        except Exception as e:
            # Clean up files in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"Error in upload_file: {str(e)}")  # Debug print
            return jsonify({"error": str(e)}), 500


@app.route("/video/<filename>")
def serve_video(filename):
    try:
        print(f"Serving video: {filename}")
        return send_from_directory(
            app.config["VIDEO_FOLDER"], filename, mimetype="video/mp4"
        )
    except Exception as e:
        print(f"Error serving video {filename}: {str(e)}")
        return jsonify({"error": f"Video not found: {filename}"}), 404


@app.route("/download/<filename>")
def download_video(filename):
    try:
        print(f"Downloading video: {filename}")
        return send_from_directory(
            app.config["VIDEO_FOLDER"],
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4",
        )
    except Exception as e:
        print(f"Error downloading video {filename}: {str(e)}")
        return jsonify({"error": f"Video not found: {filename}"}), 404


# Cleanup function to remove old videos
def cleanup_old_videos():
    current_time = time.time()
    for filename in os.listdir(app.config["VIDEO_FOLDER"]):
        filepath = os.path.join(app.config["VIDEO_FOLDER"], filename)
        if (
            os.path.getmtime(filepath) < current_time - 3600
        ):  # Remove files older than 1 hour
            os.remove(filepath)


if __name__ == "__main__":
    app.run(debug=True)
