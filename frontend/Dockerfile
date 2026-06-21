# ——— Dependencies ———
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ——— Build ———
FROM node:20-alpine AS builder
WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ——— Serve ———
FROM node:20-alpine
RUN npm install -g serve

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:nodejs /app/dist /dist

USER appuser
EXPOSE 3000

CMD ["serve", "-s", "/dist", "-l", "3000"]
