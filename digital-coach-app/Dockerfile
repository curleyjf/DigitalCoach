# --- Stage 2: Install Dependencies only when needed --- 
# Base image is node alpine image to keep the image size small 
FROM node:20-alpine AS deps

# Alpine is very lightweight and may be missing some libraries needed to build some npm packages
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app

# Install dependencies specified in package.json
# yarn.lock is included to ensure consistent versions of packages are installed
COPY package.json yarn.lock ./
# frozen-lockfile ensures that yarn installs dependencies exactly as specified in yarn.lock
RUN yarn install --frozen-lockfile

# --- Stage 2: Build source code only when needed ---
# Use lightweight Node.js base image 
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy the dependencies installed from stage 1 over to this image
COPY --from=deps /app/node_modules ./node_modules

# Copy all frontend source code from our local machine into this image
COPY . .

# --- Firebase Configuration ---
# Dockerfile needs to read the environment variables for Firebase configuration and HeyGen API key during build time
# We use arguments to pass these values from command line during the build process
# These areguments will be passed using the docker-compose file
ARG NEXT_PUBLIC_FIREBASE_API_KEY
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID
ARG NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ARG NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ARG NEXT_PUBLIC_FIREBASE_APP_ID
ARG NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID

# Set these arguments as environment variables so 'yarn build' can access them
ENV NEXT_PUBLIC_FIREBASE_API_KEY=$NEXT_PUBLIC_FIREBASE_API_KEY
ENV NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID=$NEXT_PUBLIC_FIREBASE_PROJECT_ID
ENV NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ENV NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ENV NEXT_PUBLIC_FIREBASE_APP_ID=$NEXT_PUBLIC_FIREBASE_APP_ID
ENV NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=$NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID

# Opt-out of sending telemetry data to Next.js
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application for production
# The docker compose file will override this command in development mode to run the dev server instead
RUN yarn build

# --- Stage 3: Production image ---
# Use a lightweight Node.js base image for the production environment
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app

# Sets the environment to production
ENV NODE_ENV=production

# Disable telemtry for Next.js
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security best practice
# Create group with GID 1001 called nodejs
RUN addgroup --system --gid 1001 nodejs
# Create non-root user with UID of 1001 called nextjs
RUN adduser --system --uid 1001 nextjs

# Copy the public folder (contains assets, favicons, etc.)
COPY --from=builder /app/public ./public


# Copy the files needed to run the Next.js application from the build stage
# This makes the image smaller by excluding unnecessary source files and build tools
# yarn build generates a standalone version of the app in .next/standalone which only contains the files needed to run the app
# Set ownership of the copied files to the non-root user
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Copy the browser-side assets, e.g. CSS and client-side JavaScript from the build stage
# Set ownership of the copied files to the non-root user
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port 3000 to allow access to the application
EXPOSE 3000

# Set an environment variable that specifies the port the Next.js application will listen to
ENV PORT=3000

# Set an environment variable to tell the Next.js application to listen to all network interfaces. This enables access to the Next.js application from outside the container.
ENV HOST="0.0.0.0"

# Start the Next.js application using the Node.js serverwhen the container starts
# server.js is generated from 'yarn build' as part of the standalone build
CMD ["node", "server.js"]