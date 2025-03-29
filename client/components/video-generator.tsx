"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Music, Type, MonitorSmartphone, Smartphone, Monitor, Loader2, Sparkles } from "lucide-react"
import { CherryBlossom } from "./cherry-blossom"

type VideoFormat = "youtube" | "horizontal" | "vertical"
type VideoType = "lyrics" | "music"

export default function VideoGenerator() {
  const [videoType, setVideoType] = useState<VideoType>("lyrics")
  const [videoFormat, setVideoFormat] = useState<VideoFormat>("youtube")
  const [generating, setGenerating] = useState(false)
  const [brightness, setBrightness] = useState([50])
  const [contrast, setContrast] = useState([50])
  const [textSize, setTextSize] = useState([50])

  const handleGenerate = () => {
    setGenerating(true)

    // Simulate generation process
    setTimeout(() => {
      setGenerating(false)
    }, 3000)
  }

  return (
    <div className="space-y-8">
      <div className="text-center relative">
        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2">
          <CherryBlossom className="w-8 h-8 text-pink-400 animate-float-blossom" variant="full" />
        </div>
        <h2 className="text-2xl font-bold text-pink-700 mb-2">Customize Your Video</h2>
        <p className="text-gray-600 font-medium">Choose your video type and customize settings</p>
      </div>

      <Tabs defaultValue="type" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-6 bg-white/50 rounded-xl p-1">
          <TabsTrigger
            value="type"
            className="rounded-lg data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
          >
            Video Type
          </TabsTrigger>
          <TabsTrigger
            value="format"
            className="rounded-lg data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
          >
            Format
          </TabsTrigger>
          <TabsTrigger
            value="style"
            className="rounded-lg data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
          >
            Style
          </TabsTrigger>
        </TabsList>

        <TabsContent value="type" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card
              className={`cursor-pointer transition-all ${
                videoType === "lyrics"
                  ? "border-3 border-pink-400 bg-white/70 shadow-md"
                  : "hover:border-pink-200 hover:bg-white/50 bg-white/30"
              } rounded-2xl overflow-hidden group relative`}
              onClick={() => setVideoType("lyrics")}
            >
              {videoType === "lyrics" && (
                <div className="absolute -right-3 -top-3">
                  <CherryBlossom className="w-7 h-7 text-pink-400 animate-float-blossom" variant="simple" />
                </div>
              )}
              <CardContent className="p-6 flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-pink-100 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Type className="h-8 w-8 text-pink-500" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-pink-700">Lyrics Background Video</h3>
                <p className="text-sm text-gray-600 font-medium">
                  Create a beautiful video with your song lyrics displayed over cherry blossom visuals
                </p>
              </CardContent>
            </Card>

            <Card
              className={`cursor-pointer transition-all ${
                videoType === "music"
                  ? "border-3 border-pink-400 bg-white/70 shadow-md"
                  : "hover:border-pink-200 hover:bg-white/50 bg-white/30"
              } rounded-2xl overflow-hidden group relative`}
              onClick={() => setVideoType("music")}
            >
              {videoType === "music" && (
                <div className="absolute -right-3 -top-3">
                  <CherryBlossom className="w-7 h-7 text-pink-400 animate-float-blossom" variant="full" />
                </div>
              )}
              <CardContent className="p-6 flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-pink-100 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Music className="h-8 w-8 text-pink-500" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-pink-700">Music Video</h3>
                <p className="text-sm text-gray-600 font-medium">
                  Generate a dynamic music video with cherry blossom visuals synchronized to your audio
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="format" className="space-y-6">
          <RadioGroup
            defaultValue="youtube"
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
            onValueChange={(value) => setVideoFormat(value as VideoFormat)}
          >
            <div className="flex items-start space-x-2">
              <RadioGroupItem value="youtube" id="youtube" className="mt-1 text-pink-500 border-pink-300" />
              <Label htmlFor="youtube" className="flex flex-col gap-2 cursor-pointer">
                <div className="flex items-center gap-2">
                  <Monitor className="h-4 w-4 text-pink-500" />
                  <span className="text-pink-700 font-bold">YouTube (16:9)</span>
                </div>
                <div className="w-full aspect-video bg-white/50 rounded-xl border border-pink-100 shadow-sm"></div>
                <span className="text-xs text-gray-500 font-medium">Best for YouTube and standard video platforms</span>
              </Label>
            </div>

            <div className="flex items-start space-x-2">
              <RadioGroupItem value="horizontal" id="horizontal" className="mt-1 text-pink-500 border-pink-300" />
              <Label htmlFor="horizontal" className="flex flex-col gap-2 cursor-pointer">
                <div className="flex items-center gap-2">
                  <MonitorSmartphone className="h-4 w-4 text-pink-500" />
                  <span className="text-pink-700 font-bold">Horizontal (4:3)</span>
                </div>
                <div className="w-full aspect-[4/3] bg-white/50 rounded-xl border border-pink-100 shadow-sm"></div>
                <span className="text-xs text-gray-500 font-medium">Classic format for various platforms</span>
              </Label>
            </div>

            <div className="flex items-start space-x-2">
              <RadioGroupItem value="vertical" id="vertical" className="mt-1 text-pink-500 border-pink-300" />
              <Label htmlFor="vertical" className="flex flex-col gap-2 cursor-pointer">
                <div className="flex items-center gap-2">
                  <Smartphone className="h-4 w-4 text-pink-500" />
                  <span className="text-pink-700 font-bold">Vertical (9:16)</span>
                </div>
                <div className="w-full aspect-[9/16] bg-white/50 rounded-xl border border-pink-100 shadow-sm"></div>
                <span className="text-xs text-gray-500 font-medium">Perfect for TikTok, Reels and Stories</span>
              </Label>
            </div>
          </RadioGroup>
        </TabsContent>

        <TabsContent value="style" className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label className="text-pink-700 font-bold">Brightness</Label>
                <span className="text-sm text-gray-500 font-medium">{brightness}%</span>
              </div>
              <Slider
                defaultValue={[50]}
                max={100}
                step={1}
                value={brightness}
                onValueChange={setBrightness}
                className="[&>span:first-child]:bg-pink-100"
                thumbClassName="bg-pink-500 border-pink-200 h-5 w-5"
                trackClassName="bg-pink-400 h-2"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label className="text-pink-700 font-bold">Contrast</Label>
                <span className="text-sm text-gray-500 font-medium">{contrast}%</span>
              </div>
              <Slider
                defaultValue={[50]}
                max={100}
                step={1}
                value={contrast}
                onValueChange={setContrast}
                className="[&>span:first-child]:bg-pink-100"
                thumbClassName="bg-pink-500 border-pink-200 h-5 w-5"
                trackClassName="bg-pink-400 h-2"
              />
            </div>

            {videoType === "lyrics" && (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label className="text-pink-700 font-bold">Text Size</Label>
                  <span className="text-sm text-gray-500 font-medium">{textSize}%</span>
                </div>
                <Slider
                  defaultValue={[50]}
                  max={100}
                  step={1}
                  value={textSize}
                  onValueChange={setTextSize}
                  className="[&>span:first-child]:bg-pink-100"
                  thumbClassName="bg-pink-500 border-pink-200 h-5 w-5"
                  trackClassName="bg-pink-400 h-2"
                />
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      <div className="flex justify-center pt-4 relative">
        <div className="absolute -left-6 top-1/2 transform -translate-y-1/2">
          <CherryBlossom className="w-8 h-8 text-pink-400 animate-float-blossom" variant="petal" />
        </div>
        <Button
          size="lg"
          onClick={handleGenerate}
          disabled={generating}
          className="bg-gradient-to-r from-pink-400 to-pink-600 hover:from-pink-500 hover:to-pink-700 text-white rounded-full px-8 py-6 font-bold shadow-lg hover:shadow-xl transition-all"
        >
          {generating ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-5 w-5" />
              Generate {videoType === "lyrics" ? "Lyrics Video" : "Music Video"}
            </>
          )}
        </Button>
        <div className="absolute -right-6 top-1/2 transform -translate-y-1/2">
          <CherryBlossom className="w-8 h-8 text-pink-400 animate-float-blossom" variant="full" />
        </div>
      </div>
    </div>
  )
}

