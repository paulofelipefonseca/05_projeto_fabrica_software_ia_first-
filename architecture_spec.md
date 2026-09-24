Olá! Como seu **Requirements Copilot Sênior**, meu objetivo é transformar a sua ideia inicial em uma especificação técnica clara, organizada e pronta para ser desenvolvida por qualquer equipe de engenharia de software.

O seu briefing inicial é direto: **uma página web de captura de leads (clientes) com persistência em banco de dados.**

Para garantir o sucesso do projeto, dividi esta análise em:
1. **Especificação de Requisitos (Funcionais e Não-Funcionais)**
2. **Regras de Negócio**
3. **User Stories (Histórias de Usuário)**
4. **Perguntas de Refinamento (para alinharmos os detalhes)**

---

### 1. ESPECIFICAÇÃO DE REQUISITOS

#### Requisitos Funcionais (RF) - *O que o sistema deve fazer*
*   **RF01 - Formulário de Captura:** O sistema deve apresentar um formulário na página principal contendo os seguintes campos básicos:
    *   Nome Completo (Texto)
    *   E-mail (E-mail)
    *   Telefone/WhatsApp (Numérico com máscara)
    *   *Checkbox* de consentimento de uso de dados (LGPD).
*   **RF02 - Validação de Dados:** O sistema deve validar os campos antes do envio (ex: e-mail válido, telefone com DDD, campos obrigatórios preenchidos).
*   **RF03 - Persistência de Dados:** O sistema deve salvar as informações capturadas em um banco de dados relacional ou não-relacional.
*   **RF04 - Feedback de Envio:** O sistema deve exibir uma mensagem de sucesso (ou redirecionar para uma página de "Obrigado") após o envio correto dos dados.
*   **RF05 - Tratamento de Erros:** O sistema deve alertar o usuário caso ocorra uma falha de conexão ou erro ao salvar os dados, sem perder as informações já digitadas.

#### Requisitos Não-Funcionais (RNF) - *Como o sistema deve se comportar*
*   **RNF01 - Segurança e Privacidade (LGPD):** Os dados devem ser transmitidos via protocolo seguro (HTTPS). O banco de dados deve armazenar a data, hora e o consentimento do usuário para fins de conformidade com a LGPD.
*   **RNF02 - Responsividade:** A página de captura (Landing Page) deve ser 100% responsiva, funcionando perfeitamente em dispositivos móveis (smartphones), tablets e desktops.
*   **RNF03 - Desempenho (Performance):** A página deve carregar em menos de 2 segundos (ideal para evitar a perda de leads por lentidão).
*   **RNF04 - Escalabilidade/Disponibilidade:** O backend e o banco de dados devem ser hospedados em ambiente de nuvem (ex: AWS, Supabase, Firebase ou Vercel) para garantir alta disponibilidade.

---

### 2. REGRAS DE NEGÓCIO (RN)
*   **RN01 - Duplicidade de Leads:** O sistema não deve criar um novo registro se o e-mail informado já existir no banco de dados. *Alternativa:* Atualizar os dados do lead existente e registrar uma nova data de interação.
*   **RN02 - Consentimento Obrigatório:** O botão de "Enviar/Cadastrar" só deve ser habilitado se o usuário marcar a caixa de aceite dos Termos de Privacidade/LGPD.

---

### 3. USER STORIES (HISTÓRIAS DE USUÁRIO)

#### **US01 - Cadastro de Lead (Visão do Cliente)**
> **Como um** visitante da página,
> **Eu quero** preencher meus dados de contato e demonstrar interesse,
> **Para que** a empresa possa entrar em contato comigo ou me enviar a oferta prometida.
*   **Critérios de Aceite:**
    *   O formulário deve ser simples e rápido de preencher.
    *   Devo receber uma confirmação visual clara de que meus dados foram enviados.

#### **US02 - Visualização de Leads (Visão do Administrador)**
> **Como** gestor comercial/dono do negócio,
> **Eu quero** que os dados dos clientes fiquem salvos de forma organizada,
> **Para que** eu possa acessá-los e iniciar o processo de vendas.

---

### 4. PERGUNTAS DE REFINAMENTO (Para o nosso próximo passo)

Para que eu possa detalhar ainda mais o escopo e sugerir a melhor arquitetura técnica, por favor, me responda:

1.  **Campos do Formulário:** Os campos que listei (Nome, E-mail, Telefone) são suficientes ou você precisa de mais informações (ex: Cargo, Tamanho da Empresa, Mensagem)?
2.  **Destino dos Dados:** Você quer apenas salvar no banco de dados para exportar depois (ex: em Excel/CSV), ou gostaria que esses dados fossem enviados automaticamente para um CRM (como RD Station, Hubspot, ActiveCampaign) ou para o seu e-mail?
3.  **Identidade Visual:** Você já possui um design, logotipo ou paleta de cores definida, ou precisaremos criar a identidade visual do zero?
4.  **Página de Obrigado:** Após o cadastro, o cliente deve apenas ver uma mensagem na tela ou ser redirecionado para uma nova página (ou link de WhatsApp)?

---

**Como você gostaria de prosseguir?** Se preferir, podemos ajustar os requisitos acima ou responder a essas perguntas para fecharmos a especificação técnica!