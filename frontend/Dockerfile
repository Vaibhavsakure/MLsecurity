FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# --- Production stage ---
FROM node:20-alpine AS production

WORKDIR /app

# Install serve for production static hosting
RUN npm install -g serve

# Copy built assets
COPY --from=build /app/dist ./dist

EXPOSE 4173

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:4173/ || exit 1

CMD ["serve", "-s", "dist", "-l", "4173"]
