"use client"

import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function AuthCallbackPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    console.log("[Callback] Session status:", status)
    console.log("[Callback] Session data:", session)

    const exchangeTokenWithBackend = async () => {
      try {
        console.log("[Callback] Starting token exchange with backend")
        
        // Get the backend API URL from environment variable
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        console.log("[Callback] Backend URL:", backendUrl)
        
        // Get the session to retrieve the ID token
        const response = await fetch("/api/auth/session")
        const sessionData = await response.json()
        console.log("[Callback] Session from /api/auth/session:", sessionData)
        console.log("[Callback] session.id_token exists:", !!sessionData?.id_token)

        if (sessionData?.id_token) {
          console.log("[Callback] Sending ID token to backend")
          
          // Send ID token to backend for verification and JWT issuance
          const backendResponse = await fetch(
            `${backendUrl}/api/v1/auth/google`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                id_token: sessionData.id_token,
              }),
            }
          )

          console.log("[Callback] Backend response status:", backendResponse.status)
          console.log("[Callback] Backend response ok:", backendResponse.ok)

          if (backendResponse.ok) {
            const data = await backendResponse.json()
            console.log("[Callback] Backend response body:", data)
            
            // Store the backend JWT token
            localStorage.setItem("access_token", data.access_token)
            console.log("[Callback] JWT stored in localStorage successfully")
            
            // Redirect to dashboard
            console.log("[Callback] Redirecting to dashboard")
            router.push("/dashboard")
          } else {
            const errorText = await backendResponse.text()
            console.error("[Callback] Backend error response:", errorText)
            setError("Failed to authenticate with backend")
          }
        } else {
          console.error("[Callback] No ID token found in session")
          setError("No ID token found in session")
        }
      } catch (err) {
        console.error("[Callback] Token exchange error:", err)
        setError("Failed to exchange token with backend")
      }
    }

    if (status === "loading") {
      console.log("[Callback] Waiting for session to load...")
      return // Wait for session to load
    }

    if (!session) {
      console.log("[Callback] No session, redirecting to sign-in")
      // No session, redirect to sign-in
      router.push("/auth/signin")
      return
    }

    console.log("[Callback] Session loaded, starting token exchange")
    // Exchange token with backend
    exchangeTokenWithBackend()
  }, [session, status, router])

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-md">
          <div className="rounded-md bg-red-50 p-4 mb-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button
            onClick={() => router.push("/auth/signin")}
            className="w-full rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Back to Sign In
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-gray-600">Completing authentication...</div>
    </div>
  )
}
