# Script de Deploy para AgentOS API (PowerShell)
# Este script automatiza o processo de build e deploy da aplicação

$ErrorActionPreference = "Stop"

Write-Host "Iniciando processo de deploy..." -ForegroundColor Green

try {
    # 1. Build da imagem Docker
    Write-Host "Fazendo build da imagem Docker..." -ForegroundColor Yellow
    docker build -t agnos-api:latest .

    # 2. Tag para produção
    Write-Host "Criando tag para produção..." -ForegroundColor Yellow
    docker tag agnos-api:latest agnos-api:prod

    # 3. Deploy local para teste
    Write-Host "Testando a imagem localmente..." -ForegroundColor Yellow
    docker run -d -p 8080:80 --env-file .env --name agnos-api-deploy-test agnos-api:latest

    # Aguarda alguns segundos para o container inicializar
    Write-Host "Aguardando container inicializar..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15

    # Testa o health check
    Write-Host "Verificando health check..." -ForegroundColor Yellow
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8080/v1/health" -Method GET -TimeoutSec 10
        if ($healthResponse.status -eq "healthy") {
            Write-Host "Health check passou! API está funcionando." -ForegroundColor Green
            Write-Host "Status: $($healthResponse.status)" -ForegroundColor Cyan
            Write-Host "Timestamp: $($healthResponse.timestamp)" -ForegroundColor Cyan
        } else {
            throw "Health check retornou status: $($healthResponse.status)"
        }
    } catch {
        Write-Host "Health check falhou!" -ForegroundColor Red
        Write-Host "Logs do container:" -ForegroundColor Yellow
        docker logs agnos-api-deploy-test
        throw "Health check falhou: $_"
    }

    # Limpa o container de teste
    Write-Host "Limpando container de teste..." -ForegroundColor Yellow
    docker stop agnos-api-deploy-test
    docker rm agnos-api-deploy-test

    Write-Host "Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host "Próximos passos para produção:" -ForegroundColor Cyan
    Write-Host "   1. Faça push da imagem para seu registry" -ForegroundColor White
    Write-Host "   2. Atualize seu ambiente de produção com a nova imagem" -ForegroundColor White
    Write-Host "   3. Configure as variáveis de ambiente no ambiente de produção" -ForegroundColor White
    Write-Host "   4. Reinicie os containers em produção" -ForegroundColor White

} catch {
    Write-Host "Erro durante o deploy: $_" -ForegroundColor Red
    
    # Limpa recursos em caso de erro
    try {
        docker stop agnos-api-deploy-test 2>$null
        docker rm agnos-api-deploy-test 2>$null
    } catch {
        # Ignora erros de limpeza
    }
    
    exit 1
}