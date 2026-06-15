# 🗺️ PokéAPI FastAPI - Projeto Final EBAC

Esta é uma API desenvolvida com **FastAPI** que consome dados da PokéAPI oficial, realiza filtragem dos campos obrigatórios e armazena os registros em um banco de dados local SQLite (`pokemons.db`). O projeto conta com esteira de CI/CD automatizada via GitHub Actions, empacotamento com Docker/Poetry e diversos recursos avançados de infraestrutura.

---

## 🚀 Recursos Extras Adicionados (Bônus 💯)
Para garantir a máxima robustez e segurança da aplicação, foram implementados os seguintes requisitos recomendados:
* **Segurança Avançada:** Rotas 100% protegidas por autenticação **HTTP Basic Auth**.
* **Cache em Memória:** Sistema de cache de alta performance para evitar requisições redundantes à API externa.
* **Rate Limiting:** Proteção adaptativa contra abusos (limite de 5 requisições/min no endpoint de ID e 10 requisições/min na listagem).
* **Logs Estruturados:** Emissão de logs padronizados em formato **JSON** para auditoria.
* **Tratamento de Exceções Customizado:** Respostas de erro padronizadas contendo timestamp e metadados.

---

## 🛠️ Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior instalado.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/pokeapi-ebac.git](https://github.com/SEU_USUARIO/pokeapi-ebac.git)
   cd pokeapi-ebac
   ```

2. **Configure o arquivo de ambiente (`.env`):**
   Crie um arquivo `.env` na raiz do projeto e configure as credenciais:
   ```env
   DATABASE_URL=sqlite:///./pokemons.db
   MEU_USUARIO=admin
   MINHA_SENHA=admin
   ```

3. **Instale as dependências:**
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx slowapi pytest pytest-mock pytest-cov
   ```

4. **Inicie o servidor de desenvolvimento:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8080
   ```
   Acesse a documentação interativa (Swagger) em: http://127.0.0.1:8080/docs

---

## 🧪 Como Executar os Testes Unitários

Os testes unitários utilizam banco de dados isolado em memória e *mocking* completo para simular as respostas da PokéAPI sem depender da internet.

Para rodar os testes e gerar o **Relatório de Cobertura de Código**, execute:
```bash
python -m pytest --cov=app tests/
```

---

## 🐳 Executando com Docker

Se preferir rodar a aplicação encapsulada em um contêiner, utilize os comandos:

```bash
# Build da imagem
docker build -t pokeapi-fastapi:latest .

# Execução do contêiner
docker run -d -p 8080:8080 --env-file .env pokeapi-fastapi:latest
```

---

## 📡 Exemplos de Requisição e Resposta

### 1. Detalhes de um Pokémon por ID
* **Endpoint:** `GET /pokemons/25`
* **Autenticação:** HTTP Basic (Usuário: `admin` / Senha: `admin`)
* **Resposta de Sucesso (200 OK):**
```json
{
  "id": 25,
  "name": "pikachu",
  "height": 4,
  "weight": 60,
  "types": [
    "electric"
  ],
  "sprites": {
    "front_default": "[https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png](https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png)",
    "back_default": "[https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/25.png](https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/25.png)"
  }
}
```

### 2. Listagem Paginada
* **Endpoint:** `GET /pokemons?limit=20&offset=0`
* **Autenticação:** HTTP Basic (Usuário: `admin` / Senha: `admin`)
* **Resposta de Sucesso (200 OK):**
```json
{
  "data": [
    {
      "id": 25,
      "name": "pikachu",
      "height": 4,
      "weight": 60,
      "types": ["electric"],
      "sprites": {
        "front_default": "url...",
        "back_default": "url..."
      }
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "next": null,
    "previous": null
  }
}
```

---

## 🚀 Link de Produção (API em Produção)

A API está publicada e disponível para testes no ambiente de nuvem do Render:
* **URL Oficial:** [INSIRA_O_LINK_DO_RENDER_AQUI]