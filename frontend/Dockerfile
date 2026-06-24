FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

# Serve the build output with nginx
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# The main nginx container handles routing; this image just exports the static files
