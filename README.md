# 🍽️ Web Menu API

API RESTful desenvolvida com **Django Rest Framework** para gerenciamento de pedidos de restaurante, cardápio digital e fluxo de cozinha (KDS - Kitchen Display System).

O sistema suporta múltiplos perfis de usuário (Admin, Funcionário, Cliente) e implementa regras de negócio para pedidos na mesa (QR Code) e retirada.

## 🚀 Tecnologias

- **Python 3.11** + **Django 5**
- **Django Rest Framework (DRF)**
- **MySQL 8.0**
- **Docker** & **Docker Compose**

## ⚙️ Pré-requisitos

- [Docker](https://www.docker.com/) e [MySQL](https://www.mysql.com/) instalados

## 🛠️ Como Rodar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone git@github.com:MuriloBarros304/web-menu.git
   cd web-menu
    ```

2. **Crie o arquivo de variáveis de ambiente (.env):**
Crie um arquivo `.env` na raiz e preencha:
```env
MYSQL_DB=webmenu
MYSQL_USER=webmenu_user
MYSQL_PASSWORD=senha_para_seu_bd
MYSQL_ROOT_PASSWORD=senha_para_seu_bd
DB_HOST=db
DEBUG=1
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_HOSTS=*
```


3. **Suba os containers:**
```bash
docker compose up -d --build
```


4. **Execute as migrações e crie um superusuário:**
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```


O servidor estará rodando em: `http://localhost:8000/api/`

---

## 🔑 Autenticação

A API utiliza **Token Authentication**. Este Token pode ser obtido fazendo login.
Para rotas privadas, envie o cabeçalho:
`Authorization: Token <seu_token_aqui>`

---

## 📡 Endpoints da API

### 👤 Usuários & Autenticação

| Método | Endpoint | Descrição | Permissão |
| --- | --- | --- | --- |
| `POST` | `/api/users/login/` | Login e obtenção de Token | Pública |
| `POST` | `/api/users/register/` | Cadastro de novo usuário | Pública |
| `POST` | `/api/password_reset/` | Solicitar reset de senha (Email) | Pública |
| `GET` | `/api/users/me/` | Ver dados do próprio perfil | Logado |
| `PATCH` | `/api/users/me/` | Atualizar e-mail ou dados pessoais | Logado |
| `GET` | `/api/users/` | Listar todos os usuários | Admin |
| `POST` | `/api/users/{id}/change_type/` | Mudar tipo (Admin/Staff/Customer) | Admin |
| `POST` | `/api/users/{id}/toggle_active/` | Ativar/Desativar acesso | Admin |

### 🍔 Restaurante (Cardápio & Mesas)

| Método | Endpoint | Descrição | Permissão |
| --- | --- | --- | --- |
| `GET` | `/api/dishes/` | Listar cardápio (apenas ativos) | Pública |
| `POST` | `/api/dishes/` | Criar novo prato | Admin |
| `GET` | `/api/tables/` | Listar mesas | Admin |
| `POST` | `/api/tables/` | Criar mesa (gera código QR lógico) | Admin |

### 📝 Pedidos (Orders)

| Método | Endpoint | Descrição | Permissão |
| --- | --- | --- | --- |
| `POST` | `/api/orders/` | Criar pedido (Mesa ou Viagem) | Pública/Logado |
| `GET` | `/api/orders/` | Listar meus pedidos | Logado |
| `GET` | `/api/orders/?mode=kitchen` | **Visão da Cozinha** (Fila FIFO) | Staff |
| `PATCH` | `/api/orders/{id}/mark_ready/` | Marcar pedido como "Pronto" | Staff |
| `PATCH` | `/api/orders/{id}/mark_completed/` | Finalizar pedido | Staff |

---

## 🧠 Regras de Negócio Principais

1. **Pedidos na Mesa (Dine-in):**
* Exige o ID da mesa e o `validation_code` (simulando a leitura de um QR Code físico).
* Se o código não bater com o da mesa, o pedido é rejeitado (Segurança).
* Entra com status `queued` (Na fila).


2. **Pedidos para Viagem (Takeaway):**
* Exige que o usuário esteja **logado**.
* Entra com status `pending` (Aguardando pagamento/confirmação).


3. **Fluxo da Cozinha (FIFO):**
* A rota `/api/orders/?mode=kitchen` retorna apenas pedidos com status `queued` ou `preparing`.
* Ordenação estrita por data de criação (First-In, First-Out).


4. **Gerenciamento de Preços:**
* O frontend envia apenas a quantidade e o ID do prato.
* O backend busca o preço atual no banco de dados para evitar fraudes no payload JSON.



---

## 🧪 Rodando os Testes

Para garantir a integridade das regras de negócio (Permissões, Fluxo de Pedidos, Segurança):

```bash
docker compose exec web python manage.py test

```

---

## 📂 Estrutura do Projeto

* **setup/**: Configurações globais do Django (`settings.py`, `urls.py`).
* **users/**: App responsável por Auth, Perfis e Reset de Senha.
* **restaurant/**: App Core (Pratos, Mesas, Pedidos).