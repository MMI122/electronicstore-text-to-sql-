### Build static frontend and serve with nginx
FROM node:18-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
COPY frontend/ /app
RUN npm ci --silent
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
