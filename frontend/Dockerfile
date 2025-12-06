FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Build arg for API URL (must be set at build time for Next.js)
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Build Next.js app
RUN npm run build

# Expose port and start
EXPOSE 3000
CMD ["npm", "start"]
