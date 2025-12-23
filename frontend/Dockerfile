FROM node:20-slim AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps --omit=dev

COPY --from=builder /app/.next ./.next

COPY --from=builder /app/public ./public

COPY next.config.js ./

EXPOSE 3000

CMD ["npm", "start"]
