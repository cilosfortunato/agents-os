-- Script SQL para criar a tabela de mensagens no Supabase
-- Execute este script no SQL Editor do Supabase

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhorar performance das consultas
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Índice composto para consultas por usuário e sessão
CREATE INDEX IF NOT EXISTS idx_messages_user_session ON messages(user_id, session_id);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_messages_updated_at 
    BEFORE UPDATE ON messages 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comentários para documentação
COMMENT ON TABLE messages IS 'Tabela para armazenar histórico de mensagens entre usuários e agentes';
COMMENT ON COLUMN messages.id IS 'Identificador único da mensagem';
COMMENT ON COLUMN messages.user_id IS 'Identificador do usuário';
COMMENT ON COLUMN messages.session_id IS 'Identificador da sessão de conversa';
COMMENT ON COLUMN messages.agent_id IS 'Identificador do agente que respondeu';
COMMENT ON COLUMN messages.user_message IS 'Mensagem enviada pelo usuário';
COMMENT ON COLUMN messages.agent_response IS 'Resposta gerada pelo agente';
COMMENT ON COLUMN messages.created_at IS 'Data e hora de criação da mensagem';
COMMENT ON COLUMN messages.updated_at IS 'Data e hora da última atualização';