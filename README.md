Crie um projeto completo em Flask chamado “MemoriaViva”, com a seguinte proposta e estrutura técnica:

🎯 OBJETIVO:
Desenvolver uma plataforma web chamada **MemóriaViva — Acervo Digital da Cultura Popular**, voltada à preservação e divulgação de manifestações culturais regionais.  
O sistema deve permitir cadastrar, visualizar e discutir **pessoas, tradições, histórias, eventos e patrimônios culturais**.

---

### 🧩 ARQUITETURA E PADRÕES:
- **Framework:** Flask (Python 3.10+)
- **Banco:** SQLite + SQLAlchemy
- **Migrações:** Alembic
- **Frontend:** Bootstrap 5 + Jinja2
- **Estrutura MVC:** (Models, Views/Controllers, Templates)
- **Blueprints:** `auth`, `content`, `community`, `users`, `timeline`
- **Extensões:** Flask-Login, Flask-WTF, Flask-Migrate, Flask-Bcrypt
- **Organização:**


---

### 📚 MÓDULOS E FUNCIONALIDADES:

#### 1. **Auth (Autenticação e Usuários)**
- Cadastro, login e logout
- Criptografia de senha com Flask-Bcrypt
- Papéis: `visitante`, `pesquisador`, `artista`, `admin`
- Perfis com foto, biografia e lista de contribuições

#### 2. **Content (Conteúdos Culturais)**
- CRUD de artigos, relatos, entrevistas e fotos
- Cada conteúdo pertence a uma categoria (ex: “Tradições”, “Culinária”, “Artesanato”)
- Possibilidade de anexar imagens (upload para `/static/uploads`)
- Visualização com contador de visitas

#### 3. **Categorias**
- CRUD simples para organizar os conteúdos
- Exemplo de categorias iniciais: Tradições, Festas, Culinária, Artesanato, Religião, Folclore

#### 4. **Comunidades**
- Tópicos de discussão por tema cultural
- Postagens e comentários encadeados
- Associação opcional a uma categoria cultural

#### 5. **Linha do Tempo**
- CRUD de marcos históricos (ano, evento, descrição, imagem opcional)
- Exibição cronológica em ordem crescente
- Página `/timeline` com cards Bootstrap estilizados

---

### 💾 MODELOS DO BANCO (SQLAlchemy):

**User**
- id, nome, email, senha_hash, papel, bio, foto_perfil

**Article**
- id, titulo, conteudo, categoria_id, autor_id, data_publicacao, midia_id

**Category**
- id, nome, descricao

**Media**
- id, tipo (‘imagem’, ‘áudio’, ‘vídeo’), caminho_arquivo, descricao

**Community**
- id, nome, descricao, criador_id

**Comment**
- id, conteudo, autor_id, artigo_id (ou comunidade_id), data

**Event**
- id, titulo, descricao, data_evento, local, imagem

**Timeline**
- id, ano, titulo, descricao, imagem

---

### 🎨 INTERFACE E DESIGN:
- Layout responsivo com **Bootstrap 5**
- Navbar com acesso rápido: Início | Conteúdos | Comunidades | Linha do Tempo | Login
- Templates principais:
- `base.html` (layout geral)
- `index.html` (página inicial com destaques culturais)
- `content_list.html`, `content_detail.html`
- `community_list.html`, `timeline.html`, `user_profile.html`
- Tema: tons terrosos e bege (inspirado em cultura popular)
- Ícones via **Bootstrap Icons**

---

### 🔐 SEGURANÇA:
- Senhas com hash Bcrypt
- Login protegido por Flask-Login
- Controle de acesso por papel (decoradores)
- Validação de formulários com Flask-WTF

---

### 📈 EXTRAS:
- Busca por título e categoria
- Contagem de visualizações por artigo
- Painel do administrador para gerenciar usuários e categorias
- Sistema de comentários com AJAX básico

As funcionalidades acima foram implementadas. Para rodar:

1. Instale dependências
   - `pip install -r requirements.txt`
2. Execute a aplicação
   - `python run.py`
3. Acesse `http://localhost:5000`

---

🚀 Gere o código completo do projeto, com:
- `run.py` configurado para rodar a aplicação
- Inicialização do banco e migrações automáticas
- Páginas base criadas com HTML + Bootstrap
- Rotas básicas funcionais para cada módulo
