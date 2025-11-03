# 使用 Node 镜像
FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# 构建生产版本
RUN npm run build

# 使用 Nginx 提供静态文件
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]