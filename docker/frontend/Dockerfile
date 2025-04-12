# Use a lightweight Node.js image
FROM node:18-alpine as npm

# Set working directory
WORKDIR /app

ARG REACT_APP_API_HOST
ENV REACT_APP_API_HOST=$REACT_APP_API_HOST

# Install dependencies
COPY react-dashboard/package*.json ./
RUN npm install --legacy-peer-deps

# Copy the React project
COPY react-dashboard/public ./public
COPY react-dashboard/src ./src

# Build the React app
RUN npm run build

FROM caddy:builder-alpine AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/duckdns 

FROM caddy:alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy

# Copy built frontend files to Caddy's web root
COPY --from=npm /app/build /srv

# Expose Caddy's ports
EXPOSE 80
EXPOSE 443
