"use client"

import { ProtectedRoute } from "@/components/auth/protected-route"
import Dashboard from "../dashboard"

export default function Page() {
  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  )
}
