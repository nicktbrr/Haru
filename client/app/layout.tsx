import type React from "react"
import "./globals.css"
import { Quicksand } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"

const quicksand = Quicksand({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-quicksand",
})

export const metadata = {
  title: "Haru - Cherry Blossom Video Generator",
  description: "Transform your music into beautiful videos inspired by cherry blossoms",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${quicksand.variable} font-sans bg-fixed bg-cover bg-center`}
        style={{ backgroundImage: 'url("/images/cherry-blossom-bg.png")' }}
      >
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}



import './globals.css'