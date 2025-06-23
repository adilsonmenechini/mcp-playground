# MCP Playground

Este é um playground para o Model Context Protocol (MCP) que fornece uma integração robusta com o Datadog através de interfaces web e CLI.

## 🌟 Funcionalidades

- Interface web interativa usando Streamlit
- Cliente CLI para interações via terminal
- Integração completa com Datadog
- Suporte a múltiplos modelos de LLM
- Comunicação em tempo real via SSE (Server-Sent Events)

## 🏗️ Arquitetura

O projeto é composto por dois componentes principais:

### Clientes

1. **UI Streamlit** (`/clients/ui-streamlit/`)
   - Interface web interativa
   - Chat com agente IA
   - Histórico de conversas
   - Execução de ferramentas MCP
   - Configurações dinâmicas

2. **CLI Chatbot** (`/clients/cli-chatbot/`)
   - Interface em linha de comando
   - Mesmas funcionalidades da UI web

### Servidores

1. **MCP Datadog** (`/servers/mcp-datadog/`)
   - Integração com API Datadog
   - Monitoramento (APM, métricas, logs)
   - Gerenciamento de incidentes
   - SLOs e verificações de serviço
   - Administração (usuários, funções, tags)

2. **MCP User DB** (`/servers/mcp-user-db/`)
   - Gerenciamento de usuários
   - Base de dados local

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd mcp-playground
```

2. Configure as variáveis de ambiente:
```bash
# Para o servidor Datadog
cp servers/mcp-datadog/.env.template servers/mcp-datadog/.env
# Edite o arquivo .env com suas credenciais do Datadog

# Para o cliente UI
cp clients/ui-streamlit/.env-examples clients/ui-streamlit/.env
# Edite o arquivo .env com suas configurações

# Para o cliente CLI
cp clients/cli-chatbot/.env-examples clients/cli-chatbot/.env
# Edite o arquivo .env com suas configurações
```

3. Inicie os serviços usando Docker Compose:
```bash
docker-compose up -d
```

## 💻 Uso

### Interface Web

1. Acesse a interface web em `http://localhost:8501`
2. Use o chat para interagir com o agente
3. Execute ferramentas do Datadog através dos comandos

### Cliente CLI

1. Execute o cliente CLI:
```bash
cd clients/cli-chatbot
python main.py
```

2. Digite seus comandos no terminal

## 🔧 Ferramentas Disponíveis

### Monitoramento
- APM (Application Performance Monitoring)
- Métricas e dashboards
- Logs e traces
- Hosts e serviços

### Gerenciamento de Incidentes
- Criação e gestão de alertas
- Gerenciamento de incidentes
- Análise de causa raiz
- Downtime programado

### SLOs e Qualidade
- Definição e monitoramento de SLOs
- Verificações de serviço
- Gestão de dependências
- Métricas de latência e erro

### Administração
- Gestão de usuários e funções
- Gerenciamento de tags
- Políticas de configuração
- Métricas de uso

## 🔌 Portas

- UI Streamlit: 8501
- Servidor MCP Datadog: 8101

## 📚 Documentação

A documentação completa das ferramentas do Datadog está disponível em `/servers/mcp-datadog/docs/modules.md`.

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.