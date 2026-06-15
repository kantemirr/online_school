# Dev-режим: Vite dev-server с HMR (для разработки и скриншотов ВКР).
# Прод-сборку (multi-stage → nginx) добавим на Этапе 14.
FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
