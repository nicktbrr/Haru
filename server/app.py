from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure upload settings
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..")
app.config["MUSIC_FOLDER"] = os.path.join(
    app.config["UPLOAD_FOLDER"], "assets", "music")

# Create music folder if it doesn't exist
os.makedirs(app.config["MUSIC_FOLDER"], exist_ok=True)


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
        return jsonify({"error": "Invalid file type. Only MP3 and WAV files are allowed."}), 400

    if file:
        try:
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["MUSIC_FOLDER"], filename)
            file.save(filepath)

            return jsonify({
                "message": "File uploaded successfully",
                "filename": filename,
                "filepath": filepath
            })
        except Exception as e:
            return jsonify({"error": f"Error saving file: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
