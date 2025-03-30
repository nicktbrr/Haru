import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get("audio") as File

  if (!file) {
    return NextResponse.json({ error: "No file uploaded" }, { status: 400 })
  }

  // Here you would typically save the file to a storage service
  // For this example, we'll just simulate a successful upload
  console.log("File received:", file.name)

  return NextResponse.json({ message: "File uploaded successfully" })
}

