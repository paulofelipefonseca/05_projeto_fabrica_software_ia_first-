Olá! Como seu **Requirements Copilot Sênior**, meu objetivo é transformar essa sua necessidade inicial em uma especificação técnica e funcional clara, robusta e pronta para ser desenvolvida por qualquer equipe de engenharia de software.

O seu briefing é direto, mas esconde várias nuances importantes (segurança, LGPD, experiência do usuário e arquitetura de dados). 

Para começarmos, dividi nossa análise em **três partes**:
1. **Perguntas de Descoberta** (para refinarmos o escopo).
2. **Esboço Inicial de Requisitos** (Funcionais, Não-Funcionais e Regras de Negócio).
3. **Histórias de Usuário (User Stories)** preliminares.

---

### 1. PERGUNTAS DE DESCOBERTA (Para refinar o escopo)
Para que eu possa detalhar o projeto com precisão, como você responderia a estas questões?

1. **Quais dados você quer capturar?** (Ex: Apenas Nome e E-mail? Ou também Telefone, Empresa, Cargo, Segmento?)
2. **O que acontece após o cliente clicar em "Enviar"?** (Ex: Ele vê uma mensagem de sucesso na tela? É redirecionado para outra página? Recebe um e-mail automático de boas-vindas?)
3. **Existe alguma ferramenta que você já usa?** (Ex: Quer integrar direto com um CRM como RD Station, HubSpot, ou enviar para uma planilha do Google Sheets além do banco de dados?)
4. **Quem vai acessar esses dados salvos?** (Precisamos de uma "área administrativa" simples para você visualizar e exportar os clientes capturados, ou a equipe de TI vai extrair direto do banco?)
5. **Identidade Visual:** Você já tem um logotipo, cores definidas ou um protótipo (wireframe), ou precisamos desenhar do zero?

---

### 2. ESBOÇO DA ESPECIFICAÇÃO DE REQUISITOS

Enquanto você pensa nas respostas acima, já estruturei a base técnica do seu projeto seguindo as melhores práticas de Engenharia de Requisitos:

#### **Requisitos Funcionais (RF)**
*   **RF-001: Formulário de Captura:** O sistema deve apresentar um formulário web responsivo contendo os campos: Nome Completo, E-mail, Telefone (com máscara de DDD) e um checkbox de consentimento de privacidade.
*   **RF-002: Validação de Dados:** O sistema deve validar os campos em tempo real (ex: impedir envio de e-mail sem "@", telefone incompleto ou campos obrigatórios vazios).
*   **RF-003: Persistência de Dados:** O sistema deve gravar os dados capturados em um banco de dados relacional (ex: PostgreSQL/MySQL) ou não-relacional (ex: MongoDB), registrando também a data e hora do cadastro.
*   **RF-004: Prevenção de Duplicidade:** O sistema deve verificar se o e-mail informado já existe no banco de dados. Se existir, deve atualizar o cadastro existente ou alertar o usuário (a definir na Regra de Negócio).
*   **RF-005: Feedback ao Usuário:** Após o envio bem-sucedido, o sistema deve exibir uma mensagem de sucesso amigável na tela (ou redirecionar para uma página de "Obrigado").

#### **Requisitos Não-Funcionais (RNF)**
*   **RNF-001: Segurança e LGPD (Crucial):** A página deve utilizar protocolo HTTPS (criptografia SSL). O banco de dados deve armazenar o consentimento explícito do usuário para cumprir a Lei Geral de Proteção de Dados (LGPD).
*   **RNF-002: Responsividade:** A página de captura deve ser *Mobile-First* (funcionar perfeitamente em celulares, tablets e computadores).
*   **RNF-003: Desempenho (Performance):** A página deve carregar em menos de 2 segundos em conexões 4G para evitar a perda de leads (taxa de rejeição).
*   **RNF-004: Disponibilidade:** A aplicação deve ser hospedada em ambiente de nuvem (ex: AWS, Vercel, Heroku) com disponibilidade mínima de 99.9%.

#### **Regras de Negócio (RN)**
*   **RN-001: Consentimento Obrigatório:** O botão de "Enviar" só deve ser habilitado se o usuário marcar a caixa de seleção aceitando os Termos de Privacidade e Uso de Dados.
*   **RN-002: Unicidade de Lead:** O campo "E-mail" será a chave única. Não deve haver duas linhas no banco de dados com o mesmo e-mail.

---

### 3. HISTÓRIAS DE USUÁRIO (USER STORIES)

Para a equipe de desenvolvimento (ou para você estimar o esforço):

> **US01 – Captura de Lead**
> **Como** visitante da página,
> **Eu quero** preencher meus dados de contato e enviar o formulário,
> **Para que** eu possa demonstrar interesse no produto/serviço e receber o contato da empresa.
> *Critérios de Aceite:*
> * O formulário deve validar se o e-mail é válido.
> * O botão de envio só funciona após o aceite da política de privacidade.
> * Deve aparecer uma mensagem de sucesso clara após o envio.

> **US02 – Armazenamento Seguro**
> **Como** administrador do negócio,
> **Eu quero** que os dados dos clientes sejam salvos de forma estruturada e segura em um banco de dados,
> **Para que** minha equipe comercial possa acessá-los sem risco de perda de informações.
> *Critérios de Aceite:*
> * Cada registro deve conter: ID único, Nome, E-mail, Telefone, Data/Hora do cadastro e IP de origem (para fins de auditoria da LGPD).

---

### Como deseja prosseguir?
Você prefere que eu **detalhe a modelagem do banco de dados** (tabelas e campos), ou quer que foquemos em responder às **perguntas de descoberta** para fechar o escopo exato?