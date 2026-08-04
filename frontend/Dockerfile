# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with BuildKit cache
# --mount=type=cache: Use Docker BuildKit cache for npm to avoid re-downloading unchanged packages
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Copy application source code
COPY . .

# Build-time variables for Next.js
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the application
RUN npm run build

# Stage 2: Production image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Set environment variables
# NODE_ENV: Set to production for optimized builds
# PORT: Default Next.js port
ENV NODE_ENV=production \
    PORT=3000

# Create a non-root user for security
# Running as root is a security risk in production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output from builder stage
# Standalone output includes only necessary files, significantly reducing image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
USER nextjs

# Expose Next.js default port
EXPOSE 3000

# Healthcheck to verify Next.js server is responding
# Checks root endpoint (/) every 30s with 10s timeout, 3 retries before marking unhealthy
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=5s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the application using the standalone server
CMD ["node", "server.js"]
