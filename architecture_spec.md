Olá! Como seu **Requirements Copilot Sênior**, meu objetivo é transformar essa sua necessidade inicial em uma especificação de requisitos clara, técnica, sem ambiguidades e pronta para ser desenvolvida por uma equipe de engenharia de software.

O seu pedido é um clássico cenário de **Landing Page de Captura de Leads (Geração de Demanda)** com persistência de dados. Embora pareça simples, para garantir o sucesso do projeto, precisamos detalhar o escopo.

Abaixo, apresento uma **primeira versão do Documento de Requisitos (Draft)** baseada em boas práticas e, em seguida, uma série de **perguntas de refinamento** para fecharmos o escopo.

---

# 📋 DOCUMENTO DE REQUISITOS (DRAFT V1.0)

## 1. Visão Geral do Sistema
O sistema consistirá em uma página web (Landing Page) responsiva focada na conversão de visitantes em potenciais clientes (leads). Os dados preenchidos no formulário de captura serão validados e armazenados de forma segura em um banco de dados relacional ou não-relacional.

---

## 2. Requisitos Funcionais (RF)

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| **RF-001** | **Formulário de Captura** | O sistema deve apresentar um formulário na página principal para captura de dados do usuário. | Essencial |
| **RF-002** | **Validação de Campos** | O sistema deve validar os campos antes do envio (ex: e-mail válido, telefone com DDD, campos obrigatórios preenchidos). | Essencial |
| **RF-003** | **Persistência de Dados** | O sistema deve gravar os dados capturados no banco de dados após o clique no botão de envio. | Essencial |
| **RF-004** | **Feedback de Sucesso** | O sistema deve exibir uma mensagem de sucesso amigável (ou redirecionar para uma página de "Obrigado") após o envio dos dados. | Essencial |
| **RF-005** | **Consentimento (LGPD)** | O sistema deve conter um checkbox obrigatório de aceite dos Termos de Privacidade/LGPD. | Essencial |

---

## 3. Requisitos Não-Funcionais (RNF)

| ID | Categoria | Requisito / Critério de Aceite | Prioridade |
| :--- | :--- | :--- | :--- |
| **RNF-001** | **Responsividade** | A página web deve ser *Mobile-First* (funcionar perfeitamente em smartphones, tablets e desktops). | Alta |
| **RNF-002** | **Desempenho** | A página deve carregar em menos de 2 segundos em conexões 4G estáveis (foco em SEO e conversão). | Alta |
| **RNF-003** | **Segurança** | Toda a comunicação deve ser criptografada via HTTPS (SSL). | Alta |
| **RNF-004** | **Segurança** | O banco de dados não deve expor credenciais no código do front-end (uso de API/Backend intermediário). | Alta |
| **RNF-005** | **Disponibilidade** | A aplicação deve ser hospedada em ambiente Cloud (ex: AWS, Vercel, Heroku) com disponibilidade de 99.9%. | Média |

---

## 4. Regras de Negócio (RN)

*   **RN-001 (Duplicidade):** O sistema não deve permitir o cadastro de dois leads com o mesmo endereço de e-mail. Caso ocorra, deve atualizar o registro existente ou informar que o e-mail já está cadastrado (a definir).
*   **RN-002 (LGPD):** Os dados do cliente só podem ser gravados se o checkbox de consentimento de uso de dados estiver marcado.

---

# 🔍 PERGUNTAS DE REFINAMENTO (Para refinar o escopo)

Para que eu possa gerar a especificação técnica final (User Stories, Modelo de Dados e Arquitetura), por favor, responda às seguintes questões:

1.  **Quais dados você quer capturar?**
    *   *(Exemplo padrão: Nome, E-mail, Telefone/WhatsApp, Empresa, Cargo)*
2.  **O que acontece após o cliente se cadastrar?**
    *   Ele apenas vê uma mensagem de "Obrigado"?
    *   Ele recebe um e-mail automático de confirmação?
    *   Ele é redirecionado para baixar um arquivo (ex: um PDF/E-book) ou para um grupo de WhatsApp?
3.  **Você precisa de uma área administrativa (Painel) para ver esses clientes cadastrados?**
    *   *Opção A:* Sim, preciso de uma tela com login para ver a lista de clientes e exportar para Excel.
    *   *Opção B:* Não, os dados podem ir direto para o banco e eu extraio via consulta técnica.
    *   *Opção C:* Quero que esses dados sejam enviados automaticamente para uma planilha do Google Sheets ou ferramenta de CRM (ex: RD Station, Hubspot).
4.  **Existe alguma preferência tecnológica?**
    *   *Frontend:* React, Vue, HTML/CSS puro, WordPress?
    *   *Backend/Banco de Dados:* Node.js, Python, PostgreSQL, MySQL, Firebase?
    *   *(Se não tiver preferência, eu posso sugerir a arquitetura mais eficiente e barata).*

---

**Como deseja proceder?** Pode responder às perguntas acima ou me dizer se quer ajustar algum ponto do rascunho inicial!