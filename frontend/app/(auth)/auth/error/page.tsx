"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { useRouter } from "next/navigation"

function AuthErrorContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const error = searchParams.get("error") || "Unknown error"

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-md">
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <h2 className="text-sm font-semibold text-red-800 mb-2">Authentication Error</h2>
          <p className="text-sm text-red-700">{error}</p>
        </div>
        <button
          onClick={() => router.push("/signin")}
          className="w-full rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        >
          Back to Sign In
        </button>
      </div>
    </div>
  )
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center">Loading...</div>}>
      <AuthErrorContent />
    </Suspense>
  )
}
