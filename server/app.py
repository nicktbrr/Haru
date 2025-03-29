from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    send_from_directory,
)
import os
from werkzeug.utils import secure_filename
from gemini_connector import (
    GeminiMusicAnalyzer,
    LumaAIConnector,
    generate_video,
)
import tempfile
import requests
from urllib.parse import urlparse
import time
from lumaai import LumaAI

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
app.config["VIDEO_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets/videos")

# Create video folder if it doesn't exist
os.makedirs(app.config["VIDEO_FOLDER"], exist_ok=True)

# Initialize the analyzers
gemini_analyzer = GeminiMusicAnalyzer()
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
            description = gemini_analyzer.describe_music(filepath)
            # description = "A Jet flying over the city"
            print(description)

            # Generate video
            video_url = luma_connector.generate_video(prompt=description)

            # Download and save the video
            video_filename = f"video_{int(time.time())}.mp4"
            video_path = os.path.join(
                app.config["VIDEO_FOLDER"], video_filename
            )

            response = requests.get(video_url)
            if response.status_code == 200:
                with open(video_path, "wb") as f:
                    f.write(response.content)
            else:
                raise Exception("Failed to download video")

            # Clean up the audio file
            os.remove(filepath)

            return jsonify(
                {
                    "description": description,
                    "video_url": f"/video/{video_filename}",
                    "download_url": f"/download/{video_filename}",
                }
            )

        except Exception as e:
            # Clean up files in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": str(e)}), 500


@app.route("/video/<filename>")
def serve_video(filename):
    return send_from_directory(app.config["VIDEO_FOLDER"], filename)


@app.route("/download/<filename>")
def download_video(filename):
    return send_from_directory(
        app.config["VIDEO_FOLDER"],
        filename,
        as_attachment=True,
        download_name=filename,
    )


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
