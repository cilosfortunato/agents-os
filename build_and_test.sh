#!/bin/bash

# Script para build e teste do container Docker

echo "🐳 Iniciando build do Docker..."

# Build da imagem
docker build -t agentos:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso!"
else
    echo "❌ Erro no build do Docker"
    exit 1
fi

echo "🚀 Testando o container..."

# Para qualquer container existente
docker stop agentos-test 2>/dev/null || true
docker rm agentos-test 2>/dev/null || true

# Executa o container em background
docker run -d --name agentos-test -p 7778:7777 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
    -e MEM0_API_KEY="$MEM0_API_KEY" \
    -e X_API_KEY="$X_API_KEY" \
    agentos:latest

if [ $? -eq 0 ]; then
    echo "✅ Container iniciado com sucesso!"
else
    echo "❌ Erro ao iniciar container"
    exit 1
fi

# Aguarda o container inicializar
echo "⏳ Aguardando inicialização..."
sleep 10

# Testa o health check
echo "🔍 Testando health check..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7778/health)

if [ "$response" = "200" ]; then
    echo "✅ Health check passou! API está funcionando."
    echo "🌐 API disponível em: http://localhost:7778"
    echo "📚 Documentação em: http://localhost:7778/docs"
else
    echo "❌ Health check falhou. Código de resposta: $response"
    echo "📋 Logs do container:"
    docker logs agentos-test
    docker stop agentos-test
    docker rm agentos-test
    exit 1
fi

echo "🎉 Teste concluído com sucesso!"
echo "💡 Para parar o container: docker stop agentos-test && docker rm agentos-test"