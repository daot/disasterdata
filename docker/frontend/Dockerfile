# Use a lightweight Node.js image
FROM node:18-alpine as npm

# Set working directory
WORKDIR /app

# Set build-time environment variable
ARG REACT_APP_API_HOST
ENV REACT_APP_API_HOST=$REACT_APP_API_HOST

# Copy only package.json and lock file first to leverage caching
COPY react-dashboard/package*.json ./

# Install dependencies (this will be cached unless the package.json files change)
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY react-dashboard/public ./public
COPY react-dashboard/src ./src

# Build the React app
RUN npm run build

# Build custom Caddy with DuckDNS plugin
FROM caddy:builder-alpine AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/duckdns 

# Final image
FROM caddy:alpine

# Copy built Caddy binary
COPY --from=builder /usr/bin/caddy /usr/bin/caddy

# Copy frontend build to web root
COPY --from=npm /app/build /srv

# Expose necessary ports
EXPOSE 80
EXPOSE 443
