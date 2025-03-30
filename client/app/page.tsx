import AudioUploader from "@/components/audio-uploader";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import VideoGenerator from "@/components/video-generator";
import VideoPreview from "@/components/video-preview";
import { CherryBlossom } from "@/components/cherry-blossom";
import {
  CherryBranchLeft,
  CherryBranchRight,
} from "@/components/cherry-branches";
import { FallingPetals } from "@/components/falling-petals";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Subtle falling petals animation */}
      <FallingPetals count={12} />

      {/* Header */}
      <header className="w-full py-12 px-4 sm:px-6 lg:px-8 flex justify-center relative z-10">
        <div className="text-center">
          <div className="flex items-center justify-center mb-3">
            <CherryBlossom
              className="w-12 h-12 text-pink-500 mr-3"
              variant="full"
            />
            <h1 className="text-5xl md:text-6xl font-bold text-black">
              Haru
            </h1>
            <CherryBlossom
              className="w-12 h-12 text-pink-500 ml-3"
              variant="full"
            />
          </div>
          <p className="text-lg font-medium text-pink-700 max-w-2xl">
            Bringing music to life with Luma AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl z-10">
        <div className="bg-white/80 backdrop-filter backdrop-blur-sm rounded-3xl shadow-xl p-6 md:p-8 border border-pink-100">
          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8 bg-pink-50/70 rounded-2xl p-1">
              <TabsTrigger
                value="upload"
                className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
              >
                Upload Audio
              </TabsTrigger>
              <TabsTrigger
                value="customize"
                className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
              >
                Customize Video
              </TabsTrigger>
              <TabsTrigger
                value="preview"
                className="rounded-xl data-[state=active]:bg-white data-[state=active]:text-pink-700 data-[state=active]:shadow-md font-bold"
              >
                Preview & Download
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-4">
              <AudioUploader />
            </TabsContent>

            <TabsContent value="customize" className="space-y-4">
              <VideoGenerator />
            </TabsContent>

            <TabsContent value="preview" className="space-y-4">
              <div className="grid grid-cols-1 gap-8">
                <VideoPreview
                  title="Lyrics Background Video"
                  videoType="lyrics"
                />
                <VideoPreview title="Music Video" videoType="music" />
              </div>
            </TabsContent>
          </Tabs>

          <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2">
            <CherryBlossom className="w-12 h-12 text-pink-400" variant={4} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-6 px-4 text-center text-pink-700 bg-white/70 backdrop-filter backdrop-blur-sm z-10 border-t border-pink-100 mt-8">
        <div className="flex items-center justify-center mb-2">
          <CherryBlossom
            className="w-6 h-6 text-pink-400 mx-1"
            variant="full"
          />
          <CherryBlossom
            className="w-6 h-6 text-pink-400 mx-1"
            variant="simple"
          />
          <CherryBlossom
            className="w-6 h-6 text-pink-400 mx-1"
            variant="petal"
          />
        </div>
        <p className="font-medium">
          © {new Date().getFullYear()} Haru Video Generator. All rights
          reserved.
        </p>
      </footer>
    </div>
  );
}
