"""
Módulo para aplicar migrações pendentes na inicialização da aplicação
"""
from sqlalchemy import text

def apply_content_migration(db):
    """
    Aplica a migração para adicionar colunas file_path e file_type à tabela tb_contents
    
    Args:
        db: Instância do SQLAlchemy
    """
    try:
        # Verificar se as colunas já existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'tb_contents' not in inspector.get_table_names():
            print("⚠️ Tabela tb_contents não existe ainda. Será criada pelo db.create_all()")
            return
        
        columns = [col['name'] for col in inspector.get_columns('tb_contents')]
        
        needs_migration = False
        
        # Adicionar cnt_file_path se não existir
        if 'cnt_file_path' not in columns:
            print("📝 Adicionando coluna cnt_file_path...")
            db.session.execute(text('ALTER TABLE tb_contents ADD COLUMN cnt_file_path VARCHAR(500)'))
            needs_migration = True
        
        # Adicionar cnt_file_type se não existir
        if 'cnt_file_type' not in columns:
            print("📝 Adicionando coluna cnt_file_type...")
            db.session.execute(text('ALTER TABLE tb_contents ADD COLUMN cnt_file_type VARCHAR(10)'))
            needs_migration = True
        
        if needs_migration:
            db.session.commit()
            print("✅ Migração aplicada com sucesso!")
        else:
            print("✓ Banco de dados já está atualizado")
            
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {e}")
        db.session.rollback()
        raise

def apply_ratings_migration(db):
    """
    Aplica a migração para adicionar coluna review à tabela tb_ratings
    
    Args:
        db: Instância do SQLAlchemy
    """
    try:
        # Verificar se as colunas já existem
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'tb_ratings' not in inspector.get_table_names():
            print("⚠️ Tabela tb_ratings não existe ainda. Será criada pelo db.create_all()")
            return
        
        columns = [col['name'] for col in inspector.get_columns('tb_ratings')]
        
        # Adicionar rat_review se não existir
        if 'rat_review' not in columns:
            print("📝 Adicionando coluna rat_review...")
            db.session.execute(text('ALTER TABLE tb_ratings ADD COLUMN rat_review TEXT'))
            db.session.commit()
            print("✅ Campo rat_review adicionado com sucesso!")
        else:
            print("✓ Campo rat_review já existe na tabela tb_ratings")
            
    except Exception as e:
        print(f"❌ Erro ao aplicar migração de ratings: {e}")
        db.session.rollback()
        raise

def apply_all_migrations(db):
    """
    Aplica todas as migrações pendentes
    
    Args:
        db: Instância do SQLAlchemy
    """
    print("🔄 Aplicando migrações...")
    apply_content_migration(db)
    apply_ratings_migration(db)
    try:
        # Adicionar cnt_views_count em tb_contents se não existir
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'tb_contents' in tables:
            columns = [col['name'] for col in inspector.get_columns('tb_contents')]
            if 'cnt_views_count' not in columns:
                db.session.execute(text('ALTER TABLE tb_contents ADD COLUMN cnt_views_count INTEGER DEFAULT 0 NOT NULL'))
                db.session.commit()
                print('✅ Campo cnt_views_count adicionado em tb_contents')

        # Adicionar usr_role em tb_users se não existir
        if 'tb_users' in tables:
            user_columns = [col['name'] for col in inspector.get_columns('tb_users')]
            if 'usr_role' not in user_columns:
                db.session.execute(text("ALTER TABLE tb_users ADD COLUMN usr_role VARCHAR(32) DEFAULT 'visitante' NOT NULL"))
                db.session.commit()
                print("✅ Coluna usr_role adicionada em tb_users")

        # Criar tabelas ausentes (SQLite: CREATE TABLE IF NOT EXISTS)
        if 'tb_media' not in tables:
            db.session.execute(text(
                'CREATE TABLE IF NOT EXISTS tb_media ('
                'med_id INTEGER PRIMARY KEY, '
                'med_type VARCHAR(20) NOT NULL, '
                'med_path VARCHAR(500) NOT NULL, '
                'med_description TEXT)'
            ))
            db.session.commit()
            print('✅ Tabela tb_media criada')

        if 'tb_events' not in tables:
            db.session.execute(text(
                'CREATE TABLE IF NOT EXISTS tb_events ('
                'evt_id INTEGER PRIMARY KEY, '
                'evt_title VARCHAR(255) NOT NULL, '
                'evt_description TEXT, '
                'evt_date DATE, '
                'evt_location VARCHAR(255), '
                'evt_image VARCHAR(500))'
            ))
            db.session.commit()
            print('✅ Tabela tb_events criada')

        if 'tb_timeline' not in tables:
            db.session.execute(text(
                'CREATE TABLE IF NOT EXISTS tb_timeline ('
                'tl_id INTEGER PRIMARY KEY, '
                'tl_year INTEGER NOT NULL, '
                'tl_title VARCHAR(255) NOT NULL, '
                'tl_description TEXT, '
                'tl_image VARCHAR(500), '
                'tl_created_at DATETIME NOT NULL)'
            ))
            db.session.commit()
            print('✅ Tabela tb_timeline criada')
    except Exception as e:
        print(f"❌ Erro ao aplicar migração de views_count: {e}")
        db.session.rollback()
    print("✅ Todas as migrações aplicadas!")