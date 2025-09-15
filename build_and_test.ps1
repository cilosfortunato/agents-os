# Script PowerShell para build e teste do container Docker

Write-Host "🐳 Iniciando build do Docker..." -ForegroundColor Cyan

# Build da imagem
docker build -t agentos:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no build do Docker" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Testando o container..." -ForegroundColor Cyan

# Para qualquer container existente
docker stop agentos-test 2>$null
docker rm agentos-test 2>$null

# Carrega variáveis de ambiente do .env
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Executa o container em background
$dockerCmd = @(
    "run", "-d", "--name", "agentos-test", "-p", "7778:7777",
    "-e", "OPENAI_API_KEY=$env:OPENAI_API_KEY",
    "-e", "OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY", 
    "-e", "MEM0_API_KEY=$env:MEM0_API_KEY",
    "-e", "X_API_KEY=$env:X_API_KEY",
    "agentos:latest"
)

& docker @dockerCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Container iniciado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao iniciar container" -ForegroundColor Red
    exit 1
}

# Aguarda o container inicializar
Write-Host "⏳ Aguardando inicialização..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Testa o health check
Write-Host "🔍 Testando health check..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:7778/health" -UseBasicParsing -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "Health check passou! API está funcionando." -ForegroundColor Green
        Write-Host "API disponível em: http://localhost:7778" -ForegroundColor Cyan
        Write-Host "Documentação em: http://localhost:7778/docs" -ForegroundColor Cyan
        
        # Mostra o conteúdo da resposta
        $content = $response.Content | ConvertFrom-Json
        Write-Host "Status: $($content.status)" -ForegroundColor Green
        Write-Host "Agentes: $($content.agents_count)" -ForegroundColor Green
    } else {
        throw "Código de resposta inesperado: $($response.StatusCode)"
    }
}
catch {
    Write-Host "Health check falhou: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Logs do container:" -ForegroundColor Yellow
    docker logs agentos-test
    docker stop agentos-test
    docker rm agentos-test
    exit 1
}

Write-Host "Teste concluido com sucesso!" -ForegroundColor Green
Write-Host "Para parar o container: docker stop agentos-test; docker rm agentos-test" -ForegroundColor Yellow