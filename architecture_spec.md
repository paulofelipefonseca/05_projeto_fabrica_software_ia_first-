Olá! Eu sou o seu **Requirements Copilot**. Como especialista sênior em Engenharia de Requisitos, vou transformar a sua necessidade inicial em uma especificação técnica e funcional estruturada, seguindo as melhores práticas do mercado (como os padrões IREB e BABOK).

O seu pedido é o clássico cenário de **Landing Page de Captura de Leads (Geração de Demanda)**. 

Para que este projeto seja bem-sucedido, seguro e escalável, estruturei os requisitos iniciais abaixo. Além disso, no final, farei algumas perguntas estratégicas para refinarmos o escopo.

---

# 📑 DOCUMENTO DE ESPECIFICAÇÃO DE REQUISITOS (Versão Preliminar 1.0)

## 1. Escopo do Projeto
Desenvolvimento de uma página web responsiva (Landing Page) focada na conversão de visitantes em leads, com um formulário de captura de dados integrado a um banco de dados relacional ou não-relacional, respeitando as diretrizes de segurança e privacidade (LGPD).

---

## 2. Atores do Sistema
*   **Visitante (Lead):** Usuário que acessa a página e preenche o formulário.
*   **Administrador (Opcional - a confirmar):** Usuário que visualiza os dados capturados.

---

## 3. Requisitos Funcionais (RF)

| ID | Requisito Funcional | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| **RF-001** | **Formulário de Captura** | O sistema deve apresentar um formulário na página contendo os campos: Nome Completo, E-mail, Telefone (WhatsApp) e um campo de aceite de termos. | Alta |
| **RF-002** | **Validação de Campos** | O sistema deve validar os campos antes do envio: <br>- *Nome:* Mínimo de 3 caracteres.<br>- *E-mail:* Formato válido (ex: user@domain.com).<br>- *Telefone:* Máscara de telefone válida.<br>- *Consentimento:* Obrigatório marcar o checkbox de aceite. | Alta |
| **RF-003** | **Persistência de Dados** | Ao clicar em "Enviar", o sistema deve salvar as informações validadas no banco de dados, incluindo a data e hora do registro e o IP do usuário (para fins de auditoria da LGPD). | Alta |
| **RF-004** | **Feedback de Sucesso** | Após o salvamento bem-sucedido, o sistema deve exibir uma mensagem de sucesso na tela ou redirecionar o usuário para uma "Página de Obrigado". | Alta |
| **RF-005** | **Prevenção de Duplicidade** | O sistema deve verificar se o e-mail preenchido já existe no banco de dados. Se sim, deve atualizar os dados do lead em vez de criar um novo registro (ou impedir o novo cadastro, conforme regra de negócio). | Média |

---

## 4. Requisitos Não-Funcionais (RNF)

| ID | Requisito Não-Funcional | Categoria | Descrição | Prioridade |
| :--- | :--- | :--- | :--- | :--- |
| **RNF-001** | **Responsividade (Mobile-First)** | Usabilidade | A página deve ser 100% responsiva, adaptando-se perfeitamente a dispositivos móveis, tablets e desktops. | Alta |
| **RNF-002** | **Segurança da Informação** | Segurança | O tráfego de dados deve ser criptografado via protocolo HTTPS (certificado SSL ativo). | Alta |
| **RNF-003** | **Prevenção de Ataques** | Segurança | O backend deve implementar sanitização de inputs para evitar ataques de *SQL Injection* e *XSS (Cross-Site Scripting)*. | Alta |
| **RNF-004** | **Desempenho (Performance)** | Eficiência | A página deve carregar em menos de 2 segundos sob condições normais de internet, visando otimização para SEO e conversão. | Média |
| **RNF-005** | **Privacidade (LGPD)** | Conformidade | O sistema deve registrar formalmente o consentimento do usuário para o tratamento dos dados, em conformidade com a Lei Geral de Proteção de Dados. | Alta |

---

## 5. Regras de Negócio (RN)

*   **RN-001 (Política de Consentimento):** O formulário não pode ser enviado se o usuário não marcar o checkbox declarando que leu e aceita a Política de Privacidade.
*   **RN-002 (Notificação de Lead):** (Opcional) A cada novo cadastro, um e-mail de alerta deve ser enviado para o administrador da página, ou um e-mail de boas-vindas deve ser disparado para o lead.

---

## 6. Modelo Conceitual do Banco de Dados (Sugestão Inicial)
Para salvar estes dados, sugiro uma tabela simples chamada `leads`:

*   `id` (INT, Chave Primária, Auto-incremento)
*   `nome` (VARCHAR 100, Obrigatório)
*   `email` (VARCHAR 100, Obrigatório, Único)
*   `telefone` (VARCHAR 20, Opcional/Obrigatório)
*   `consentimento_lgpd` (BOOLEAN, Obrigatório - True)
*   `criado_em` (DATETIME, preenchido automaticamente)
*   `ip_origem` (VARCHAR 45)

---

# ❓ PERGUNTAS DE REFINAMENTO (Para o cliente)

Para que eu possa detalhar ainda mais o seu projeto, por favor, responda às seguintes perguntas:

1.  **Quais campos específicos você quer capturar?** (Ex: Apenas Nome e E-mail? Ou precisa de Telefone, Empresa, Cargo?)
2.  **Haverá integração com alguma ferramenta?** (Ex: Você quer que os dados fiquem apenas no seu banco de dados, ou quer que eles sejam enviados automaticamente para um CRM como RD Station, Hubspot, ou ActiveCampaign?)
3.  **Como você pretende visualizar esses dados depois?** Precisa de um painel administrativo (Dashboard) para ver os clientes capturados ou prefere exportar os dados em Excel/CSV?
4.  **Você já tem uma identidade visual, logotipo ou textos prontos?**
5.  **Qual é a tecnologia de sua preferência?** (Ex: WordPress, React + Node.js, HTML/CSS puro com PHP, etc.)

---

Como deseja prosseguir? Podemos refinar os requisitos com base nas suas respostas ou focar em desenhar a estrutura do banco de dados agora.