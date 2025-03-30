"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Download, Play, Pause, Volume2, VolumeX } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type VideoPreviewProps = {
  title: string;
  videoType: "lyrics" | "music";
  videoUrl?: string | null;
};

export default function VideoPreview({
  title,
  videoType,
  videoUrl,
}: VideoPreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState([80]);
  const [progress, setProgress] = useState([0]);
  const [quality, setQuality] = useState("720p");
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16">("16:9");
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleVideoLoad = () => {
    if (videoRef.current) {
      const { videoWidth, videoHeight } = videoRef.current;
      const ratio = videoWidth / videoHeight;
      setAspectRatio(ratio > 1 ? "16:9" : "9:16");
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (value: number[]) => {
    if (videoRef.current) {
      videoRef.current.volume = value[0] / 100;
      setVolume(value);
    }
  };

  const handleProgressChange = (value: number[]) => {
    if (videoRef.current) {
      const time = (value[0] / 100) * videoRef.current.duration;
      videoRef.current.currentTime = time;
      setProgress(value);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold text-pink-700">{title}</h3>
      <div className="relative">
        <div
          className={`bg-gray-800 rounded-xl overflow-hidden shadow-lg ${
            aspectRatio === "16:9"
              ? "aspect-video w-full"
              : "aspect-[9/16] w-[360px] mx-auto"
          }`}
        >
          <video
            ref={videoRef}
            src={`/assets/output/output.mp4`}
            className="w-full h-full object-cover"
            onLoadedMetadata={handleVideoLoad}
            onTimeUpdate={() => {
              if (videoRef.current) {
                const progress =
                  (videoRef.current.currentTime / videoRef.current.duration) *
                  100;
                setProgress([progress]);
              }
            }}
            onEnded={() => setIsPlaying(false)}
          />
        </div>

        {/* Video Controls */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
          <div className="space-y-2">
            <Slider
              defaultValue={[0]}
              max={100}
              step={1}
              value={progress}
              onValueChange={handleProgressChange}
              className="[&>span:first-child]:h-1.5 [&>span:first-child]:bg-white/30 [&_[role=slider]]:bg-pink-400 [&_[role=slider]]:w-4 [&_[role=slider]]:h-4 [&_[role=slider]]:border-0 [&>span:first-child_span]:bg-pink-400"
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={togglePlay}
                  className="text-white hover:bg-white/20 rounded-full"
                >
                  {isPlaying ? (
                    <Pause className="h-5 w-5" />
                  ) : (
                    <Play className="h-5 w-5" />
                  )}
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleMute}
                  className="text-white hover:bg-white/20 rounded-full"
                >
                  {isMuted ? (
                    <VolumeX className="h-5 w-5" />
                  ) : (
                    <Volume2 className="h-5 w-5" />
                  )}
                </Button>

                <div className="w-24 hidden sm:block">
                  <Slider
                    defaultValue={[80]}
                    max={100}
                    step={1}
                    value={volume}
                    onValueChange={handleVolumeChange}
                    className="[&>span:first-child]:h-1 [&>span:first-child]:bg-white/30 [&_[role=slider]]:bg-pink-400 [&_[role=slider]]:w-3 [&_[role=slider]]:h-3 [&_[role=slider]]:border-0 [&>span:first-child_span]:bg-pink-400"
                  />
                </div>

                <span className="text-xs text-white font-medium">
                  0:00 / 3:45
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <Select defaultValue="720p" onValueChange={setQuality}>
                  <SelectTrigger className="h-7 w-16 text-xs bg-transparent text-white border-white/20 rounded-full">
                    <SelectValue placeholder="Quality" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1080p">1080p</SelectItem>
                    <SelectItem value="720p">720p</SelectItem>
                    <SelectItem value="480p">480p</SelectItem>
                  </SelectContent>
                </Select>

                <Button
                  size="sm"
                  className="bg-pink-500 text-white hover:bg-pink-600 h-7 px-3 text-xs rounded-full font-bold"
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
