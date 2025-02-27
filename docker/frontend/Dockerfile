# Use a lightweight Node.js image
FROM node:18

# Set working directory
WORKDIR /app

# Copy the React project
COPY react-dashboard/ .

# Install dependencies
RUN npm install --legacy-peer-deps

# Build the React app
RUN npm run build

# Use a lightweight web server (Caddy)
FROM caddy:latest

# Copy built frontend files to Caddy's web root
COPY --from=0 /app/build /srv

# Expose Caddy's ports
EXPOSE 80
EXPOSE 443
