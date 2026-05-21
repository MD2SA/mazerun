FROM node:20-alpine

WORKDIR /app

# Instalar pnpm
RUN npm install -g pnpm

# Copiar os ficheiros de dependências
COPY package.json pnpm-lock.yaml ./

# Instalar as dependências
RUN pnpm install

# Copiar o resto do código da app
COPY . .

# Expor a porta do servidor de desenvolvimento do Vite
EXPOSE 5173

# Correr o Vite em modo desenvolvimento. 
# O --host é necessário no Docker para que a app fique acessível fora do contentor
CMD ["pnpm", "run", "dev", "--host"]
