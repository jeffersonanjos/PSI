# app/blueprints/content.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from ..models import Content, Rating, db, Category, ContentCategory
import os
from werkzeug.utils import secure_filename
import uuid

content_bp = Blueprint('content', __name__, url_prefix='/content')


@content_bp.route('/')
def list_content():
    """Lista todo o conteúdo disponível"""
    contents = Content.query.all()

    from ..utils.helpers import (
        extract_youtube_id,
        youtube_thumbnail_url,
        youtube_embed_url,
    )

    return render_template(
        'content/list.html',
        contents=contents,
        extract_youtube_id=extract_youtube_id,
        youtube_thumbnail_url=youtube_thumbnail_url,
        youtube_embed_url=youtube_embed_url,
    )


@content_bp.route('/buscar', methods=['GET'])
@login_required
def buscar_obra():
    termo = (request.args.get('q') or '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Content.query
    if termo:
        query = query.filter(
            db.or_(
                Content.title.ilike(f'%{termo}%'),
                Content.description.ilike(f'%{termo}%')
            )
        )
    if category_id:
        query = query.join(ContentCategory, Content.id == ContentCategory.content_id)
        query = query.filter(ContentCategory.category_id == category_id)

    resultados = query.order_by(Content.created_at.desc()).all() if (termo or category_id) else []
    categorias = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'buscar.html',
        resultados=resultados,
        termo=termo,
        categorias=categorias,
        selected_category_id=category_id
    )


@content_bp.route('/<int:content_id>')
def view_content(content_id):
    """Visualiza um conteúdo específico"""
    from sqlalchemy import func
    content = Content.query.get_or_404(content_id)

    ratings = Rating.query.filter_by(content_id=content_id).order_by(Rating.created_at.desc()).all()
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(content_id=content_id).scalar()
    total_ratings = len(ratings)

    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(
            user_id=current_user.id,
            content_id=content_id
        ).first()

    from ..utils.helpers import (
        extract_youtube_id,
        youtube_thumbnail_url,
        youtube_embed_url,
    )

    return render_template(
        'content/view.html',
        content=content,
        ratings=ratings,
        avg_rating=avg_rating,
        total_ratings=total_ratings,
        user_rating=user_rating,
        extract_youtube_id=extract_youtube_id,
        youtube_thumbnail_url=youtube_thumbnail_url,
        youtube_embed_url=youtube_embed_url,
    )


@content_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_content():
    """Cria novo conteúdo"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content_type = request.form.get('type')
        url = request.form.get('url')
        thumbnail = request.form.get('thumbnail')
        release_date = request.form.get('release_date')

        allowed_types = ['artigo', 'relato', 'entrevista', 'foto']
        if content_type not in allowed_types:
            flash('Tipo de conteúdo inválido.', 'danger')
            return render_template('content/create.html')

        has_file = request.files.get('file') and request.files.get('file').filename != ''
        has_url = url and url.strip() != ''

        if not has_file and not has_url:
            flash('É obrigatório fornecer um arquivo ou um link.', 'danger')
            return render_template('content/create.html')

        relative_path = None
        file_ext = None
        file = request.files.get('file')

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            ALLOWED_FILE_EXTS = ['pdf', 'epub', 'jpg', 'jpeg', 'png', 'webp']
            if file_ext not in ALLOWED_FILE_EXTS:
                flash('Formato de arquivo não permitido.', 'danger')
                return render_template('content/create.html')

            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)

            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            relative_path = f"uploads/obras/{unique_filename}"

        # Gera thumbnail do YouTube automaticamente se aplicável
        if not thumbnail and url:
            from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
            video_id = extract_youtube_id(url)
            if video_id:
                thumbnail = youtube_thumbnail_url(video_id, quality='maxresdefault')

        from ..utils.helpers import parse_date
        release_date_obj = parse_date(release_date)

        new_content = Content(
            title=title,
            description=description,
            type=content_type,
            url=url,
            thumbnail=thumbnail,
            release_date=release_date_obj,
            file_path=relative_path,
            file_type=file_ext,
            user_id=current_user.id
        )

        db.session.add(new_content)
        db.session.commit()

        flash('Conteúdo criado com sucesso!', 'success')
        return redirect(url_for('content.list_content'))

    return render_template('content/create.html')


@content_bp.route('/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_content(content_id):
    """Edita conteúdo existente"""
    content = Content.query.get_or_404(content_id)

    if content.user_id != current_user.id:
        flash("Você não tem permissão para editar este conteúdo.", "danger")
        return redirect(url_for('content.view_content', content_id=content_id))

    if request.method == 'POST':
        content.title = request.form.get('title')
        content.description = request.form.get('description')
        content_type = request.form.get('type')

        if content_type not in ['artigo', 'relato', 'entrevista', 'foto']:
            flash('Tipo de conteúdo inválido.', 'danger')
            return render_template('content/edit.html', content=content)

        content.type = content_type

        # Upload de novo arquivo
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext not in ['pdf', 'epub', 'jpg', 'jpeg', 'png', 'webp']:
                flash('Formato de arquivo inválido.', 'danger')
                return render_template('content/edit.html', content=content)

            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)

            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join(upload_dir, unique_filename))
            content.file_path = f"uploads/obras/{unique_filename}"
            content.file_type = ext

        # Upload da nova capa
        thumbnail_file = request.files.get('thumbnail_file')
        if thumbnail_file and thumbnail_file.filename != '':
            filename = secure_filename(thumbnail_file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'thumbnails')
                os.makedirs(upload_dir, exist_ok=True)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                thumbnail_file.save(file_path)
                new_thumbnail_url = url_for('static', filename=f'uploads/thumbnails/{unique_filename}', _external=False)
                content.thumbnail = new_thumbnail_url
            else:
                flash('Formato de capa inválido. Use JPG, PNG ou WEBP.', 'danger')

        new_url = request.form.get('url')
        content.url = new_url or content.url

        release_date = request.form.get('release_date')
        if release_date:
            from ..utils.helpers import parse_date
            content.release_date = parse_date(release_date)

        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'new_thumbnail_url': content.thumbnail}), 200

        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('content.view_content', content_id=content_id))

    return render_template('content/edit.html', content=content)


@content_bp.route('/<int:content_id>/download')
def download_content(content_id):
    """Permite o download do arquivo do conteúdo"""
    content = Content.query.get_or_404(content_id)

    if not content.file_path:
        flash('Este conteúdo não possui arquivo para download.', 'warning')
        return redirect(url_for('content.view_content', content_id=content_id))

    file_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)

    if not os.path.exists(file_full_path):
        flash('Arquivo não encontrado.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))

    return send_file(file_full_path, as_attachment=True, download_name=os.path.basename(file_full_path))


@content_bp.route('/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    """Deleta um conteúdo"""
    content = Content.query.get_or_404(content_id)

    if content.user_id != current_user.id:
        flash("Você não tem permissão para excluir este conteúdo.", "danger")
        return redirect(url_for('content.view_content', content_id=content_id))

    try:
        if content.file_path:
            file_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
            if os.path.exists(file_full_path):
                os.remove(file_full_path)

        db.session.delete(content)
        db.session.commit()
        flash('Conteúdo deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar conteúdo: {str(e)}', 'danger')

    return redirect(url_for('content.list_content'))


@content_bp.route('/<int:content_id>/rate', methods=['POST'])
@login_required
def rate_content(content_id):
    """Permite que o usuário avalie o conteúdo"""
    rating_value = request.form.get('rating', type=int)
    if not rating_value or rating_value < 1 or rating_value > 5:
        flash('Avaliação inválida. Escolha uma nota de 1 a 5.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))

    existing = Rating.query.filter_by(user_id=current_user.id, content_id=content_id).first()
    if existing:
        existing.rating = rating_value
    else:
        new_rating = Rating(user_id=current_user.id, content_id=content_id, rating=rating_value)
        db.session.add(new_rating)

    db.session.commit()
    flash('Avaliação registrada com sucesso!', 'success')
    return redirect(url_for('content.view_content', content_id=content_id))


@content_bp.route('/rating/<int:rating_id>/remove', methods=['POST'])
@login_required
def remove_rating(rating_id):
    """Permite que o usuário remova sua avaliação"""
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash('Você não tem permissão para remover esta avaliação.', 'danger')
        return redirect(url_for('content.view_content', content_id=rating.content_id))

    db.session.delete(rating)
    db.session.commit()
    flash('Avaliação removida com sucesso!', 'success')
    return redirect(url_for('content.view_content', content_id=rating.content_id))
