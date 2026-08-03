import NextAuth from "next-auth"
import Google from "next-auth/providers/google"

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  providers: [
    Google({
        clientId: process.env.GOOGLE_CLIENT_ID || "",
        clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      // Only allow Google sign-in
      if (account?.provider !== "google") {
        return false
      }
      return true
    },
    async jwt({ token, account }) {
      // Store the Google ID token in the JWT
      if (account) {
        token.id_token = account.id_token
      }
      return token
    },
    async session({ session, token }) {
      // Pass the ID token to the session
      if (token.id_token) {
        session.id_token = token.id_token as string
      }
      return session
    },
  },
  pages: {
    signIn: "/signin",
    error: "/auth/error",
  },
  session: {
    strategy: "jwt",
  },
})
