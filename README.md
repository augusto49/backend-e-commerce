# 🚀 E-commerce Backend API

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST-Framework-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Um backend robusto e escalável para plataforma de E-commerce, desenvolvido com **Django REST Framework**. Inclui gestão completa de catálogo, carrinhos, pedidos, pagamentos, integração logística e painel administrativo.

---

## 📋 Funcionalidades Principais

- **🔐 Autenticação & Segurança**: JWT (Access/Refresh), RBAC (Clientes/Admin), Proteção contra Brute-force (Axes).
- **📦 Catálogo Avançado**: Categorias hierárquicas (MPTT), variações de produtos (SKU), controle de estoque em tempo real.
- **🛒 Experiência de Compra**: Carrinho persistente (Redis), Cupons de desconto, Wishlist.
- **💳 Pagamentos Multi-Gateway**:
  - **Mercado Pago** (PIX/Cartão)
  - **Stripe**
  - Webhooks automatizados
- **🚚 Logística**: Cálculo de frete e rastreamento via **Correios** (Sedex/PAC).
- **🔔 Notificações**: Sistema de e-mails transacionais (Celery) e templates dinâmicos.
- **📊 Analytics**: Dashboard de vendas, relatórios e auditoria de ações (AuditLog).
- **⚖️ Compliance**: Adequação à LGPD (Exportação e Exclusão de dados).

---

## 🛠️ Stack Tecnológica

- **Framework**: Django 5.1 + Django REST Framework
- **Banco de Dados**: PostgreSQL 15
- **Cache & Sessão**: Redis 7
- **Tarefas Assíncronas**: Celery + Celery Beat
- **Documentação API**: Drf-spectacular (Swagger/Redoc/Scalar)
- **Infraestrutura**: Docker & Docker Compose
- **Testes**: Pytest + Factory Boy

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose instalados.

### Passo a Passo

1. **Clone o repositório**

   ```bash
   git clone https://github.com/seu-usuario/backend-e-commerce.git
   cd backend-e-commerce
   ```

2. **Configure as Variáveis de Ambiente**
   Para configurar o ambiente localmente, faça uma cópia do arquivo de exemplo:

   ```bash
   cp .env.example .env
   ```

   Em seguida, edite o arquivo `.env` com suas credenciais. As variáveis do **Correios** são opcionais para teste (use um CEP de origem válido):

   ```env
   # Exemplo
   CORREIOS_ORIGIN_CEP=01310100
   ```

3. **Inicie os Containers**

   ```bash
   docker-compose up -d --build
   ```

4. **Aplique as Migrações**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Crie um Superusuário**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

O backend estará rodando em `http://localhost:8000`.

---

## 📚 Documentação da API

A API possui documentação interativa completa gerada automaticamente. Acesse:

| Interface  | URL            | Descrição                                    |
| ---------- | -------------- | -------------------------------------------- |
| **Scalar** | `/api/docs/`   | Interface moderna e interativa (Recomendado) |
| **Redoc**  | `/api/redoc/`  | Documentação estática e organizada           |
| **Schema** | `/api/schema/` | Arquivo OpenAPI YAML/JSON                    |

---

## 🧪 Rodando os Testes

Este projeto utiliza **pytest** para testes automatizados. Para executar a suíte de testes:

```bash
# Executar todos os testes
docker-compose exec web pytest

# Executar com relatório de cobertura
docker-compose exec web pytest --cov=apps

# Executar testes específicos
docker-compose exec web pytest tests/test_orders.py -v
```

---

## 📂 Estrutura do Projeto

```
backend-e-commerce/
├── apps/               # Aplicações do domínio (core, accounts, products, etc)
├── config/             # Configurações do projeto (settings, urls)
├── tests/              # Testes automatizados (pytest)
├── docker/             # Dockerfiles e scripts
├── requirements.txt    # Dependências Python
├── manage.py           # CLI Django
└── docker-compose.yml  # Orquestração de containers
```

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
