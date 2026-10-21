"use client"

import { ReactNode } from "react"
import { useAuth } from "@/context/AuthContext"
import { useRouter } from "next/navigation"

export function RoleGuard({
  role,
  children,
}: {
  role: "teacher" | "student"
  children: ReactNode
}) {
  const { user, loading } = useAuth()
  const router = useRouter()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
      </div>
    )
  }

  if (!user || user.role !== role) {
    router.replace(user ? (user.role === "teacher" ? "/teacher" : "/student") : "/login")
    return null
  }

  return <>{children}</>
}
