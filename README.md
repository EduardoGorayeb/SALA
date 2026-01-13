# SALA — Sistema de Avaliação de Linguagem em Apresentações

O **SALA** é um sistema inteligente de análise automática de apresentações orais, desenvolvido como projeto de **TCC**, com foco em **avaliação objetiva, feedback avançado por IA e métricas próximas da realidade de bancas avaliadoras**.

O sistema processa **vídeos** (TCC, palestras, apresentações explicativas ou comerciais), extrai áudio, realiza limpeza e diarização, transcreve com IA e calcula métricas detalhadas de desempenho comunicativo, gerando um **relatório completo e profissional**.

---

## 🎯 Objetivo do Projeto

Criar uma ferramenta capaz de:

* Avaliar apresentações de forma **automática e padronizada**
* Reduzir a subjetividade de avaliações humanas
* Fornecer **feedback claro, técnico e acionável**
* Simular critérios reais de bancas avaliadoras
* Servir como base para evolução contínua do apresentador

---

## 🧠 Funcionalidades Principais

### Upload de Vídeo

* Interface web para envio de vídeos
* Loader animado durante o processamento
* Execução assíncrona do pipeline completo

### Processamento de Áudio

* Extração de áudio do vídeo
* Limpeza de ruído
* Diarização (separação por locutor)

### Transcrição Inteligente

* Transcrição automática do discurso
* Correção e refinamento via IA (Gemini)
* Padronização textual para análise

### Métricas Avaliadas

* **Velocidade de fala (WPM)**
* **Tangência ao tema**
* **Clareza e objetividade**
* **Prosódia e entonação**
* **Nervosismo**
* **Vícios de linguagem** (repetições, palavras desnecessárias)

Cada métrica é calculada separadamente e integrada a uma **nota final ponderada**.

### Tipo de Apresentação

O usuário escolhe manualmente o tipo de apresentação:

* TCC
* Palestra
* Apresentação explicativa
* Apresentação comercial

Essa informação:

* É salva no banco de dados
* Influencia as métricas
* Altera os prompts e critérios de avaliação

### Relatório Final

* Geração de relatório estruturado
* Métricas detalhadas
* Nota final
* Feedback avançado gerado por IA
* Salvamento completo em **JSON** no banco

### Histórico de Avaliações

* Listagem de análises anteriores
* Filtros e paginação
* Reutilização de dados para evolução futura

---

## 🏗️ Arquitetura do Sistema

### Backend

* **Django**

  * Gerenciamento de usuários
  * Upload de vídeos
  * Controle do fluxo
  * Persistência no banco de dados

* **Módulo Python Externo (`run_sala.py`)**

  * Executa todo o pipeline de análise
  * Processamento pesado isolado do servidor web

* **IA de Transcrição e Correção**

  * Gemini (Google)

### Banco de Dados

* Armazena:

  * Usuário
  * Tipo de apresentação
  * Transcrição
  * Métricas
  * Feedback
  * Relatório completo em JSON

---

## ⚙️ Fluxo de Funcionamento

1. Usuário faz upload do vídeo
2. Django inicia o processo assíncrono
3. `run_sala.py` executa:

   * Extração de áudio
   * Limpeza e diarização
   * Transcrição
   * Correção textual
   * Cálculo de métricas
   * Geração de feedback
4. Resultados são salvos no banco
5. Relatório é exibido no frontend

---

## 🚀 Diferenciais

* Avaliação baseada em **dados reais**, não achismo
* Arquitetura modular e escalável
* Métricas pensadas para **banca acadêmica**
* Feedback técnico + linguagem acessível
* Base sólida para evolução futura

---

## 🔮 Próximas Evoluções Planejadas

* Ajuste fino de pesos das métricas por tipo de apresentação
* Sistema de evolução do apresentador
* Geração de relatório em PDF
* Comparação entre apresentações
* Dashboard analítico

---

## 👨‍💻 Autor

Projeto desenvolvido por **Eduardo Gorayeb** como Trabalho de Conclusão de Curso, com foco em **IA aplicada à educação, comunicação e avaliação objetiva**.

---

## 📜 Licença

Este projeto está sob licença de uso educacional. Uso comercial requer autorização do autor.
