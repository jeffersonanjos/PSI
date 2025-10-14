from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Timeline as TimelineModel


timeline_bp = Blueprint('timeline', __name__, url_prefix='/timeline')


@timeline_bp.route('/')
def index():
    items = TimelineModel.query.order_by(TimelineModel.ano.asc(), TimelineModel.id.asc()).all()
    return render_template('timeline.html', items=items)


@timeline_bp.route('/create', methods=['POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Apenas administradores podem criar marcos da linha do tempo.', 'danger')
        return redirect(url_for('timeline.index'))
    
    ano = request.form.get('ano', type=int)
    titulo = (request.form.get('titulo') or '').strip()
    descricao = (request.form.get('descricao') or '').strip()
    imagem = (request.form.get('imagem') or '').strip() or None

    if not ano or not titulo:
        flash('Ano e título são obrigatórios.', 'warning')
        return redirect(url_for('timeline.index'))

    item = TimelineModel(ano=ano, titulo=titulo, descricao=descricao or None, imagem=imagem)
    db.session.add(item)
    db.session.commit()
    flash('Marco criado com sucesso!', 'success')
    return redirect(url_for('timeline.index'))


@timeline_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id: int):
    if not current_user.is_admin:
        flash('Apenas administradores podem excluir marcos.', 'danger')
        return redirect(url_for('timeline.index'))
    item = TimelineModel.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Marco excluído.', 'success')
    return redirect(url_for('timeline.index'))
