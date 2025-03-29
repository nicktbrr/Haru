"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"

export default function VideoOptions() {
  const [lyricsVideo, setLyricsVideo] = useState<string | null>(null)
  const [musicVideo, setMusicVideo] = useState<string | null>(null)

  const generateVideos = async () => {
    try {
      const response = await fetch("/api/generate-videos")
      const data = await response.json()
      setLyricsVideo(data.lyricsVideo)
      setMusicVideo(data.musicVideo)
    } catch (error) {
      console.error("Error generating videos:", error)
      alert("An error occurred while generating the videos.")
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Video Options</h2>
      <Button onClick={generateVideos} className="w-full mb-4">
        Generate Videos
      </Button>
      <div className="space-y-4">
        {lyricsVideo && (
          <div>
            <h3 className="font-medium mb-2">Lyrics Background Video</h3>
            <video src={lyricsVideo} controls className="w-full rounded-lg" />
            <a
              href={lyricsVideo}
              download="lyrics_video.mp4"
              className="inline-flex items-center space-x-2 text-purple-600 hover:text-purple-700 mt-2"
            >
              <Download size={20} />
              <span>Download</span>
            </a>
          </div>
        )}
        {musicVideo && (
          <div>
            <h3 className="font-medium mb-2">Music Video</h3>
            <video src={musicVideo} controls className="w-full rounded-lg" />
            <a
              href={musicVideo}
              download="music_video.mp4"
              className="inline-flex items-center space-x-2 text-purple-600 hover:text-purple-700 mt-2"
            >
              <Download size={20} />
              <span>Download</span>
            </a>
          </div>
        )}
      </div>
    </div>
  )
}

