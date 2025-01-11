FROM node:18-alpine

WORKDIR /app

# Copia os arquivos necessários para instalar dependências
COPY package.json package-lock.json ./

# Instala dependências com --legacy-peer-deps
RUN npm install --legacy-peer-deps

# Copia o restante dos arquivos do projeto
COPY . .

# Gera o build de produção
RUN npm run build

# Expõe a porta do frontend
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "run", "start"]
