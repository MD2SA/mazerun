# Estágio 1: Build (Compilar a app Vite)
FROM node:20-alpine AS builder

WORKDIR /app

# Instalar pnpm (usado no vosso projeto)
RUN npm install -g pnpm

# Copiar os ficheiros de dependências
COPY package.json pnpm-lock.yaml ./

# Instalar as dependências
RUN pnpm install

# Copiar o resto do código da app e fazer o build para produção
COPY . .
RUN pnpm run build

# Estágio 2: Produção (Servir a app com Nginx)
FROM nginx:alpine

# Limpar o Nginx por defeito
RUN rm -rf /usr/share/nginx/html/*

# Copiar os ficheiros estáticos do estágio de build (Vite gera a pasta 'dist')
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
