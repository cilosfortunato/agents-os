import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print('=== VERIFICANDO VARIÁVEIS DE AMBIENTE ===')
print(f'OUTBOUND_WEBHOOK_URL: {os.getenv("OUTBOUND_WEBHOOK_URL", "NÃO DEFINIDA")}')
print(f'WEBHOOK_API_KEY: {os.getenv("OUTBOUND_WEBHOOK_API_KEY", "NÃO DEFINIDA")}')
print(f'PORT: {os.getenv("PORT", "NÃO DEFINIDA")}')
print(f'SUPABASE_URL: {os.getenv("SUPABASE_URL", "NÃO DEFINIDA")}')

# Verificar se há alguma configuração hardcoded
print('\n=== VERIFICANDO CONFIGURAÇÃO NO CÓDIGO ===')
try:
    with open('api_completa.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'webhook.site' in content:
            print('❌ ENCONTRADO webhook.site hardcoded no código!')
        else:
            print('✅ Não há webhook.site hardcoded')
            
        # Buscar linha do OUTBOUND_WEBHOOK_URL
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'OUTBOUND_WEBHOOK_URL' in line and not line.strip().startswith('#'):
                print(f'Linha {i+1}: {line.strip()}')
                
except Exception as e:
    print(f'Erro ao ler arquivo: {e}')