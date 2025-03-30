import VideoPreview from "@/components/video-preview"
import { CherryBlossom } from "@/components/cherry-blossom"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function PreviewPage() {
  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-5xl relative z-10">
        <Link
          href="/"
          className="inline-flex items-center text-pink-700 hover:text-pink-800 font-medium mb-6 transition-colors"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>

        <div className="flex items-center mb-8">
          <CherryBlossom className="w-8 h-8 text-pink-500 mr-3" variant="full" />
          <h1 className="text-3xl font-bold text-pink-800">Preview & Download</h1>
        </div>

        <div className="bg-white/80 backdrop-filter backdrop-blur-sm rounded-3xl shadow-xl p-6 md:p-8 border border-pink-100 relative">
          <div className="absolute -top-5 right-10">
            <CherryBlossom className="w-10 h-10 text-pink-400" variant="full" />
          </div>

          <div className="grid grid-cols-1 gap-8">
            <VideoPreview title="Lyrics Background Video" videoType="lyrics" />
            <VideoPreview title="Music Video" videoType="music" />
          </div>

          <div className="absolute -bottom-5 left-10">
            <CherryBlossom className="w-10 h-10 text-pink-400" variant="simple" />
          </div>
        </div>
      </div>
    </div>
  )
}

