"""
Módulo para criar dados padrão: conta MemóriaViva e comunidade oficial
"""
from .models import db, Usuario, Community

def create_default_account_and_community():
    """
    Cria a conta oficial MemóriaViva e a comunidade padrão
    """
    try:
        # Verificar se a conta MemóriaViva já existe
        mv_user = Usuario.query.filter_by(email='memoriaviva@oficial').first()
        
        if not mv_user:
            print("📝 Criando conta oficial MemóriaViva...")
            mv_user = Usuario(
                nome='MemóriaViva',
                email='memoriaviva@oficial',
                is_admin=True,  # Conta oficial é administradora
                role='admin'
            )
            mv_user.senha = 'memoriaviva123'  # Usa o setter que gera hash
            db.session.add(mv_user)
            db.session.commit()
            print("✅ Conta MemóriaViva criada com sucesso!")
        else:
            print("✓ Conta MemóriaViva já existe")
        
        # Verificar se a comunidade MemóriaViva já existe
        mv_community = Community.query.filter_by(name='MemóriaViva').first()
        
        if not mv_community:
            print("📝 Criando comunidade oficial MemóriaViva...")
            mv_community = Community(
                owner_id=mv_user.id,
                name='MemóriaViva',
                description='Comunidade oficial do MemóriaViva. Participe das discussões sobre cultura popular e acervos regionais!',
                status='active',
                is_filtered=False
            )
            db.session.add(mv_community)
            db.session.commit()
            print("✅ Comunidade MemóriaViva criada com sucesso!")
        else:
            print("✓ Comunidade MemóriaViva já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados padrão: {e}")
        db.session.rollback()
        raise
