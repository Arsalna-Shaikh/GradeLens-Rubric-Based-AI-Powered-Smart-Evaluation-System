import type { Metadata } from "next"
import { Inter } from "next/font/google"
import React from "react"
import "../frontend/src/app/globals.css"
import { AuthProvider } from "../frontend/src/context/AuthContext"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "GradeLens",
  description: "Rubric-based AI-powered evaluation platform",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  )
}
