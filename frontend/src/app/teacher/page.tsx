"use client"

import { ProtectedRoute } from "@/components/ProtectedRoute"
import { RoleGuard } from "@/components/RoleGuard"
import { useAuth } from "@/context/AuthContext"

export default function TeacherDashboardPage() {
  return (
    <ProtectedRoute>
      <RoleGuard role="teacher">
        <TeacherDashboard />
      </RoleGuard>
    </ProtectedRoute>
  )
}

function TeacherDashboard() {
  const { user, logout } = useAuth()

  return (
    <main className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Teacher Dashboard</h1>
          <button
            onClick={logout}
            className="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Logout
          </button>
        </div>
        <p className="text-gray-700">Welcome, {user?.name}. Class and assignment management coming soon.</p>
      </div>
    </main>
  )
}
