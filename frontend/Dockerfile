FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Copy application files
COPY . .

# Install dependencies (will be done at runtime due to volume mount)
RUN npm install

# Expose Vite dev server port
EXPOSE 5173

# Run development server with host binding for Docker
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0"]
