from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Category, ContentCategory

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

def _require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Acesso negado. Apenas administradores.', 'danger')
        return False
    return True

@categories_bp.route('/')
@login_required
def list_categories():
    if not _require_admin():
        return redirect(url_for('main.index'))
    categorias = Category.query.order_by(Category.name.asc()).all()
    counts = {
        c.id: db.session.query(ContentCategory).filter_by(category_id=c.id).count() for c in categorias
    }
    return render_template('categories/list.html', categorias=categorias, counts=counts)

@categories_bp.route('/create', methods=['POST'])
@login_required
def create_category():
    if not _require_admin():
        return redirect(url_for('categories.list_categories'))
    nome = (request.form.get('nome') or '').strip()
    if not nome:
        flash('Nome é obrigatório.', 'warning')
        return redirect(url_for('categories.list_categories'))
    if Category.query.filter_by(name=nome).first():
        flash('Já existe uma categoria com este nome.', 'warning')
        return redirect(url_for('categories.list_categories'))
    cat = Category(name=nome)
    db.session.add(cat)
    db.session.commit()
    flash('Categoria criada!', 'success')
    return redirect(url_for('categories.list_categories'))

@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id: int):
    if not _require_admin():
        return redirect(url_for('categories.list_categories'))
    cat = Category.query.get_or_404(category_id)
    associated = db.session.query(ContentCategory).filter_by(category_id=category_id).count()
    if associated:
        flash('Não é possível excluir: existem conteúdos associados.', 'danger')
        return redirect(url_for('categories.list_categories'))
    db.session.delete(cat)
    db.session.commit()
    flash('Categoria excluída.', 'success')
    return redirect(url_for('categories.list_categories'))
