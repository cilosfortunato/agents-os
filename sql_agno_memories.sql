-- SQL para criar a tabela agno_memories no Supabase
-- Execute este código no SQL Editor do dashboard do Supabase

-- Criar a tabela principal
CREATE TABLE public.agno_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    memory TEXT NOT NULL,
    topics TEXT[] DEFAULT '{}',
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    team_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_agno_memories_user_id ON public.agno_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_agno_memories_agent_id ON public.agno_memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_agno_memories_team_id ON public.agno_memories(team_id);
CREATE INDEX IF NOT EXISTS idx_agno_memories_topics ON public.agno_memories USING GIN(topics);
CREATE INDEX IF NOT EXISTS idx_agno_memories_created_at ON public.agno_memories(created_at);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_agno_memories_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_agno_memories_updated_at ON public.agno_memories;
CREATE TRIGGER update_agno_memories_updated_at 
    BEFORE UPDATE ON public.agno_memories 
    FOR EACH ROW 
    EXECUTE FUNCTION update_agno_memories_updated_at();

-- Inserir dados de teste
INSERT INTO public.agno_memories (
    memory_id, 
    memory, 
    topics, 
    user_id, 
    agent_id
) VALUES (
    'test-memory-001',
    'Usuário prefere respostas técnicas e detalhadas',
    ARRAY['preferencias', 'estilo', 'tecnico'],
    'test-user-123',
    'test-agent-456'
);

-- Verificar se funcionou
SELECT * FROM public.agno_memories;