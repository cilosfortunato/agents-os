-- Criação da tabela agno_memories para o sistema de memórias do Agno
-- Esta tabela armazena as memórias enriquecidas dos agentes

CREATE TABLE IF NOT EXISTS public.agno_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    memory TEXT NOT NULL,
    topics TEXT[] DEFAULT '{}',
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    team_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
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

-- Comentários para documentação
COMMENT ON TABLE public.agno_memories IS 'Tabela para armazenar memórias enriquecidas dos agentes Agno';
COMMENT ON COLUMN public.agno_memories.memory_id IS 'Identificador único da memória';
COMMENT ON COLUMN public.agno_memories.memory IS 'Conteúdo da memória';
COMMENT ON COLUMN public.agno_memories.topics IS 'Array de tópicos relacionados à memória';
COMMENT ON COLUMN public.agno_memories.user_id IS 'ID do usuário associado à memória';
COMMENT ON COLUMN public.agno_memories.agent_id IS 'ID do agente que criou a memória';
COMMENT ON COLUMN public.agno_memories.team_id IS 'ID do time (opcional)';
COMMENT ON COLUMN public.agno_memories.created_at IS 'Data e hora de criação';
COMMENT ON COLUMN public.agno_memories.updated_at IS 'Data e hora da última atualização';