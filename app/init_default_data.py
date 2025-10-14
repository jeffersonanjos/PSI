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
        memoria_viva_user = Usuario.query.filter_by(email='memoriaviva@oficial').first()
        
        if not memoria_viva_user:
            print("📝 Criando conta oficial MemóriaViva...")
            memoria_viva_user = Usuario(
                nome='MemóriaViva',
                email='memoriaviva@oficial',
                is_admin=True  # Conta oficial é administradora
            )
            memoria_viva_user.senha = 'memoriaviva123'  # Usa o setter que gera hash
            db.session.add(memoria_viva_user)
            db.session.commit()
            print("✅ Conta MemóriaViva criada com sucesso!")
        else:
            print("✓ Conta MemóriaViva já existe")
        
        # Verificar se a comunidade MemóriaViva já existe
        memoria_viva_community = Community.query.filter_by(name='MemóriaViva').first()
        
        if not memoria_viva_community:
            print("📝 Criando comunidade oficial MemóriaViva...")
            memoria_viva_community = Community(
                owner_id=memoria_viva_user.id,
                name='MemóriaViva',
                description='Comunidade oficial do MemóriaViva. Participe das discussões sobre acervos, tradições e cultura popular!',
                status='active',
                is_filtered=False
            )
            db.session.add(memoria_viva_community)
            db.session.commit()
            print("✅ Comunidade MemóriaViva criada com sucesso!")
        else:
            print("✓ Comunidade MemóriaViva já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados padrão: {e}")
        db.session.rollback()
        raise
