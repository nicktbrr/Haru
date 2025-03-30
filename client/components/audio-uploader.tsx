"use client";

import type React from "react";

import { useState } from "react";
import { Music, Upload, Check, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CherryBlossom } from "./cherry-blossom";

export default function AudioUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith("audio/")) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError("Please select a valid audio file (MP3, WAV, etc.)");
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const xhr = new XMLHttpRequest();

      // Create a promise to handle the XHR request
      const uploadPromise = new Promise((resolve, reject) => {
        xhr.upload.addEventListener("progress", (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            setUploadProgress(Math.round(progress));
          }
        });

        xhr.addEventListener("load", () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(JSON.parse(xhr.response));
          } else {
            reject(
              new Error(
                xhr.response ? JSON.parse(xhr.response).error : "Upload failed"
              )
            );
          }
        });

        xhr.addEventListener("error", () => {
          reject(new Error("Upload failed"));
        });
      });

      xhr.open("POST", "http://127.0.0.1:5000/upload");
      xhr.send(formData);

      await uploadPromise;
      setUploadProgress(100);
      setUploadComplete(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center relative">
        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2">
          <CherryBlossom
            className="w-8 h-8 text-pink-400 animate-float-blossom"
            variant="full"
          />
        </div>
        <h2 className="text-2xl font-bold text-pink-700 mb-2">
          Upload Your Audio
        </h2>
        <p className="text-gray-600 font-medium">
          Upload your MP3, WAV, or other audio file to get started
        </p>
      </div>

      <div className="border-3 border-dashed border-pink-200 rounded-3xl p-10 text-center bg-white/50 transition-all hover:bg-white/70 group relative">
        <div className="absolute -right-4 -top-4">
          <CherryBlossom
            className="w-8 h-8 text-pink-400 animate-float-blossom"
            variant="simple"
          />
        </div>

        <input
          type="file"
          accept="audio/*"
          onChange={handleFileChange}
          className="hidden"
          id="audio-upload"
        />
        <label
          htmlFor="audio-upload"
          className="cursor-pointer flex flex-col items-center justify-center gap-4"
        >
          <div className="w-20 h-20 rounded-full bg-pink-100 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Music className="h-10 w-10 text-pink-500" />
          </div>
          <div className="text-sm text-gray-600">
            <p className="font-bold">Click to upload or drag and drop</p>
            <p className="font-medium">MP3, WAV, or other audio files</p>
          </div>
        </label>

        <div className="absolute -left-4 -bottom-4">
          <CherryBlossom
            className="w-8 h-8 text-pink-400 animate-float-blossom"
            variant="petal"
          />
        </div>
      </div>

      {file && (
        <div className="bg-white/70 rounded-2xl p-5 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-pink-100 flex items-center justify-center">
              <Music className="h-6 w-6 text-pink-500" />
            </div>
            <div>
              <p className="font-bold text-pink-700">{file.name}</p>
              <p className="text-sm text-pink-500 font-medium">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>
          {!uploadComplete ? (
            <Button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-pink-500 hover:bg-pink-600 text-white rounded-full px-6 font-bold shadow-md hover:shadow-lg transition-all"
            >
              {uploading ? (
                <>Uploading...</>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </>
              )}
            </Button>
          ) : (
            <div className="flex items-center text-pink-500 bg-pink-100 px-4 py-2 rounded-full">
              <Check className="mr-2 h-5 w-5" />
              <span className="font-bold">Uploaded</span>
            </div>
          )}
        </div>
      )}

      {uploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600 font-medium">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} className="h-2 bg-pink-100" />
        </div>
      )}

      {error && (
        <Alert variant="destructive" className="rounded-xl">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle className="font-bold">Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {uploadComplete && (
        <Alert className="bg-pink-50 border-pink-200 text-pink-700 rounded-xl">
          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-pink-100 mr-2">
            <Check className="h-4 w-4 text-pink-500" />
          </div>
          <AlertTitle className="font-bold">Upload Complete</AlertTitle>
          <AlertDescription className="font-medium">
            Your audio file has been uploaded successfully. You can now
            customize your video.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
