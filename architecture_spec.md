Olá! Como seu **Requirements Copilot Sênior**, meu objetivo é transformar essa sua ideia inicial em uma especificação de requisitos clara, técnica, sem ambiguidades e pronta para que qualquer equipe de desenvolvimento (ou ferramenta de IA) possa codificar sem erros.

O seu briefing inicial é direto: **uma página web de captura de leads (clientes) integrada a um banco de dados.**

Para transformarmos isso em um documento de requisitos robusto, dividi nossa interação em três partes:
1. **Primeiro Esboço de Requisitos** (o que já conseguimos deduzir como padrão de mercado).
2. **Perguntas de Elicitação** (o que preciso que você me responda para refinarmos o escopo).
3. **Próximos Passos**.

---

### 1. PRIMEIRO ESBOÇO DE REQUISITOS (Draft Técnico)

Com base nas melhores práticas de Engenharia de Requisitos e LGPD (Lei Geral de Proteção de Dados), aqui está a primeira versão dos requisitos do seu sistema:

#### **História de Usuário (User Story)**
> **Como um** Visitante do site,
> **Eu quero** preencher um formulário com meus dados de contato,
> **Para que** eu possa receber mais informações/contato da empresa.
>
> **Como um** Administrador do sistema,
> **Eu quero** que os dados dos visitantes sejam salvos de forma segura em um banco de dados,
> **Para que** eu possa gerenciar e entrar em contato com esses potenciais clientes.

#### **Requisitos Funcionais (RF)**
*   **RF-001: Formulário de Captura:** O sistema deve apresentar uma página web (Landing Page) com um formulário contendo os campos: Nome Completo, E-mail, Telefone (com DDD) e um campo de consentimento de privacidade.
*   **RF-002: Validação de Dados:** O sistema deve validar os campos antes do envio (ex: e-mail deve conter "@" e domínio válido; telefone deve aceitar apenas números; campos obrigatórios não podem ficar vazios).
*   **RF-003: Persistência de Dados:** O sistema deve gravar os dados validados no banco de dados, incluindo a data e hora do cadastro e o IP do usuário (para fins de auditoria da LGPD).
*   **RF-004: Feedback ao Usuário:** Após o envio bem-sucedido, o sistema deve exibir uma mensagem de sucesso na tela ou redirecionar o usuário para uma "Página de Obrigado".
*   **RF-005: Prevenção de Spam (Anti-bot):** O formulário deve possuir um mecanismo de proteção contra robôs (ex: reCAPTCHA ou Honeypot).

#### **Requisitos Não-Funcionais (RNF)**
*   **RNF-001: Responsividade (UX):** A página deve ser 100% responsiva, adaptando-se perfeitamente a dispositivos móveis (smartphones), tablets e desktops.
*   **RNF-002: Segurança e Privacidade (LGPD):** Os dados devem ser transmitidos via protocolo seguro HTTPS (SSL). O banco de dados deve criptografar dados sensíveis (se houver) e a página deve conter um checkbox obrigatório de aceite dos Termos de Privacidade.
*   **RNF-003: Desempenho:** A página de captura deve carregar em menos de 2 segundos sob conexões de internet padrão (4G/Banda Larga).

---

### 2. PERGUNTAS DE ELICITAÇÃO (Para refinarmos o escopo)

Para que eu possa gerar a documentação final perfeita (especificação técnica, modelo de dados e critérios de aceitação), por favor, responda às seguintes perguntas:

1.  **Campos do Formulário:** Quais dados exatos você quer capturar do cliente? (Ex: Apenas *Nome* e *E-mail*? Ou precisa de *Telefone*, *Nome da Empresa*, *Cargo*, *Mensagem*?)
2.  **Destino dos Dados (Integração):** Além de salvar no banco de dados, você gostaria que esses dados fossem enviados automaticamente para algum outro lugar? (Ex: Enviar um e-mail de notificação para você, ou integrar com ferramentas como RD Station, HubSpot, Mailchimp, WhatsApp?)
3.  **Identidade Visual / Design:** Você já tem um logotipo, cores definidas ou uma identidade visual que devemos seguir? Ou deseja que eu sugira uma estrutura padrão de alta conversão?
4.  **Acesso aos Dados:** Como você pretende visualizar os clientes capturados?
    *   *Opção A:* Diretamente acessando o banco de dados (via ferramenta técnica).
    *   *Opção B:* Precisa de uma tela administrativa simples (com login/senha) para ver a lista de clientes e exportar para Excel?
5.  **Hospedagem/Tecnologia:** Você já tem preferência por alguma tecnologia (ex: React, HTML/CSS puro, WordPress, Node.js, Python) ou serviço de nuvem (AWS, Firebase, Vercel, Hostgator)? Se não tiver, posso recomendar a mais barata e eficiente.

---

### Como você quer proceder?
Responda às perguntas acima (mesmo que de forma simples) e eu gerarei a **Especificação de Requisitos Completa** e o **Esquema do Banco de Dados (SQL)** para o seu projeto!