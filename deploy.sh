#!/bin/bash

# Script de Deploy para AgentOS API
# Este script automatiza o processo de build e deploy da aplicação

set -e  # Para o script se houver erro

echo "🚀 Iniciando processo de deploy..."

# 1. Build da imagem Docker
echo "📦 Fazendo build da imagem Docker..."
docker build -t agnos-api:latest .

# 2. Tag para produção (ajuste conforme seu registry)
echo "🏷️  Criando tag para produção..."
docker tag agnos-api:latest agnos-api:prod

# 3. Se você usar um registry (Docker Hub, AWS ECR, etc.), descomente as linhas abaixo:
# echo "📤 Fazendo push para o registry..."
# docker push agnos-api:prod

# 4. Deploy local para teste (opcional)
echo "🧪 Testando a imagem localmente..."
docker run -d -p 8080:80 --env-file .env --name agnos-api-deploy-test agnos-api:latest

# Aguarda alguns segundos para o container inicializar
sleep 10

# Testa o health check
echo "🔍 Verificando health check..."
if curl -f http://localhost:8080/v1/health > /dev/null 2>&1; then
    echo "✅ Health check passou! API está funcionando."
else
    echo "❌ Health check falhou!"
    docker logs agnos-api-deploy-test
    docker stop agnos-api-deploy-test
    docker rm agnos-api-deploy-test
    exit 1
fi

# Limpa o container de teste
echo "🧹 Limpando container de teste..."
docker stop agnos-api-deploy-test
docker rm agnos-api-deploy-test

echo "🎉 Deploy concluído com sucesso!"
echo "📋 Próximos passos para produção:"
echo "   1. Faça push da imagem para seu registry"
echo "   2. Atualize seu ambiente de produção com a nova imagem"
echo "   3. Configure as variáveis de ambiente no ambiente de produção"
echo "   4. Reinicie os containers em produção"