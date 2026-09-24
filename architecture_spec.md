Olá! Como seu **Requirements Copilot Sênior**, vou transformar o seu briefing inicial (que é uma excelente ideia de negócio, mas ainda abstrata) em uma especificação técnica e funcional estruturada. 

Para que possamos avançar para a fase de desenvolvimento com segurança, dividi nossa análise em **4 partes**:
1. **Entendimento do Escopo (Visão Geral)**
2. **Perguntas de Elucidação (Para refinarmos o projeto)**
3. **Primeiro Esboço de Requisitos (Funcionais, Não-Funcionais e Regras de Negócio)**
4. **Estrutura do Banco de Dados (Sugestão Inicial)**

---

### 1. Entendimento do Escopo (Visão Geral)
O objetivo é criar uma **Landing Page (Página de Captura)** focada em conversão. O usuário final preencherá um formulário e esses dados serão persistidos de forma segura em um banco de dados para que sua equipe possa utilizá-los posteriormente (vendas, marketing, etc.).

---

### 2. Perguntas de Elucidação (O Copilot precisa saber):
Para detalharmos o escopo exato, por favor, me responda:
1. **Quais dados você quer capturar?** (Ex: Apenas Nome e E-mail? Ou também Telefone/WhatsApp, Cargo, Nome da Empresa?)
2. **O que acontece após o cliente clicar em "Enviar"?** (Ex: Ele vê uma mensagem de sucesso na tela, é redirecionado para outra página, ou recebe um e-mail automático?)
3. **Existe alguma ferramenta de CRM que você já usa?** (Ex: RD Station, HubSpot, ActiveCampaign, ou quer salvar puramente em um banco de dados próprio como PostgreSQL/MySQL?)
4. **Precisamos de uma área administrativa?** (Uma tela com login para você visualizar e exportar esses clientes em Excel, ou você acessará direto o banco de dados?)

---

### 3. Primeiro Esboço de Requisitos

Enquanto você pensa nas respostas acima, já estruturei a primeira versão dos requisitos com base nas melhores práticas de Engenharia de Requisitos (incluindo conformidade com a **LGPD**):

#### **Requisitos Funcionais (RF)**
*   **RF-01: Formulário de Captura:** O sistema deve apresentar um formulário na página web para que o usuário insira seus dados de contato.
*   **RF-02: Validação de Campos:** O sistema deve validar os campos antes do envio (ex: garantir que o e-mail tenha formato válido `@` e que campos obrigatórios não estejam vazios).
*   **RF-03: Consentimento LGPD:** O sistema deve exibir um checkbox obrigatório de aceite dos Termos de Privacidade/Consentimento de uso de dados.
*   **RF-04: Persistência de Dados:** O sistema deve gravar os dados capturados no banco de dados com a data e hora do cadastro.
*   **RF-05: Feedback de Sucesso:** O sistema deve exibir uma mensagem de sucesso amigável após a gravação dos dados.

#### **Requisitos Não-Funcionais (RNF)**
*   **RNF-01: Responsividade (Mobile-First):** A página deve ser 100% adaptável para dispositivos móveis (smartphones e tablets).
*   **RNF-02: Segurança (HTTPS):** A página deve trafegar dados sob protocolo seguro HTTPS (certificado SSL).
*   **RNF-03: Performance:** A página deve carregar em menos de 2 segundos para evitar a perda de leads.
*   **RNF-04: Proteção contra Spam:** O formulário deve conter proteção contra robôs (ex: reCAPTCHA v3 invisível).

#### **Regras de Negócio (RN)**
*   **RN-01: Unicidade de Lead:** O sistema não deve permitir o cadastro duplicado do mesmo endereço de e-mail (ou deve atualizar o cadastro existente com a nova data de interação).

---

### 4. Sugestão de Estrutura do Banco de Dados (Tabela: `leads`)

Para salvar os dados de forma organizada, sugiro esta estrutura inicial de tabela:

| Campo | Tipo de Dado | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `id` | UUID / INT (PK) | Identificador único do lead | `1` ou `uuid-v4` |
| `nome` | VARCHAR(100) | Nome completo do cliente | `João Silva` |
| `email` | VARCHAR(150) | E-mail (Único) | `joao@email.com` |
| `telefone` | VARCHAR(20) | Telefone com DDD | `(11) 99999-9999` |
| `aceitou_lgpd` | BOOLEAN | Confirmação de aceite dos termos | `TRUE` |
| `criado_em` | TIMESTAMP | Data e hora do cadastro | `2023-10-27 14:30:00` |

---

### Próximo Passo:
Como você quer refinar essa estrutura? Responda às perguntas do **item 2** ou me diga se já podemos gerar o documento de especificação final (PRD) para enviar aos desenvolvedores!