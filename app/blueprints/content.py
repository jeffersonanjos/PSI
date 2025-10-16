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

    # Helpers do YouTube
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
    """Cria novo conteúdo (artigo, relato, entrevista ou foto)"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content_type = request.form.get('type')
        url = request.form.get('url')
        thumbnail = request.form.get('thumbnail')
        release_date = request.form.get('release_date')

        # ✅ Tipos aceitos conforme o HTML
        allowed_types = ['artigo', 'relato', 'entrevista', 'foto']
        if content_type not in allowed_types:
            flash('Tipo de conteúdo inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/create.html')

        # Validar: arquivo OU URL obrigatório
        has_file = request.files.get('file') and request.files.get('file').filename != ''
        has_url = url and url.strip() != ''

        if not has_file and not has_url:
            flash('É obrigatório fornecer um arquivo (PDF/Imagem) ou um link.', 'danger')
            return render_template('content/create.html')

        relative_path = None
        file_ext = None
        file = request.files.get('file')

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            # ✅ Extensões aceitas
            ALLOWED_FILE_EXTS = ['pdf', 'epub', 'jpg', 'jpeg', 'png', 'webp']
            if file_ext not in ALLOWED_FILE_EXTS:
                flash('Formato de arquivo não permitido. Use PDF, EPUB ou imagem (JPG/PNG/WEBP).', 'danger')
                return render_template('content/create.html')

            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)

            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)

            relative_path = f"uploads/obras/{unique_filename}"

        # Gerar thumbnail do YouTube automaticamente se for entrevista
        if not thumbnail and url:
            from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
            video_id = extract_youtube_id(url)
            if video_id:
                thumbnail = youtube_thumbnail_url(video_id, quality='maxresdefault')

        from ..utils.helpers import parse_date
        release_date_obj = parse_date(release_date)
        if release_date and not release_date_obj:
            flash('Data de publicação inválida.', 'danger')
            return render_template('content/create.html')

        new_content = Content(
            title=title,
            description=description,
            type=content_type,
            url=url,
            thumbnail=thumbnail,
            release_date=release_date_obj,
            file_path=relative_path,
            file_type=file_ext
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

    if request.method == 'POST':
        content.title = request.form.get('title')
        content.description = request.form.get('description')
        content_type = request.form.get('type')

        allowed_types = ['artigo', 'relato', 'entrevista', 'foto']
        if content_type not in allowed_types:
            flash('Tipo de conteúdo inválido. Selecione um tipo válido.', 'danger')
            return render_template('content/edit.html', content=content)

        content.type = content_type

        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            ALLOWED_FILE_EXTS = ['pdf', 'epub', 'jpg', 'jpeg', 'png', 'webp']

            if file_ext not in ALLOWED_FILE_EXTS:
                flash('Formato de arquivo não permitido. Use PDF, EPUB ou imagem (JPG/PNG/WEBP).', 'danger')
                return render_template('content/edit.html', content=content)

            if content.file_path:
                old_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'obras')
            os.makedirs(upload_dir, exist_ok=True)

            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)

            content.file_path = f"uploads/obras/{unique_filename}"
            content.file_type = file_ext

        new_url = request.form.get('url')
        content.url = new_url

        new_thumbnail = request.form.get('thumbnail')
        content.thumbnail = new_thumbnail

        if not new_thumbnail and new_url:
            from ..utils.helpers import extract_youtube_id, youtube_thumbnail_url
            video_id = extract_youtube_id(new_url)
            if video_id:
                content.thumbnail = youtube_thumbnail_url(video_id, quality='maxresdefault')

        release_date = request.form.get('release_date')
        if release_date:
            from ..utils.helpers import parse_date
            content.release_date = parse_date(release_date)

        db.session.commit()
        flash('Conteúdo atualizado com sucesso!', 'success')
        return redirect(url_for('content.view_content', content_id=content_id))

    return render_template('content/edit.html', content=content)


@content_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Upload rápido de imagem para conteúdo. Retorna URL pública."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Arquivo inválido.'}), 400

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    file_url = url_for('static', filename=f'uploads/{filename}', _external=False)
    return jsonify({'success': True, 'url': file_url})


@content_bp.route('/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    """Deleta um conteúdo"""
    content = Content.query.get_or_404(content_id)

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


@content_bp.route('/<int:content_id>/download')
@login_required
def download_content(content_id):
    """Faz download do arquivo do conteúdo"""
    content = Content.query.get_or_404(content_id)

    if not content.file_path:
        flash('Este conteúdo não possui arquivo disponível para download.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))

    file_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', content.file_path)
    if not os.path.exists(file_full_path):
        flash('Arquivo não encontrado.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))

    return send_file(file_full_path, as_attachment=True, download_name=f"{content.title}.{content.file_type}")

# ============================================================
# Sistema de avaliações
# ============================================================

@content_bp.route('/<int:content_id>/rate', methods=['POST'])
@login_required
def rate_content(content_id):
    """Adiciona ou atualiza avaliação de um conteúdo"""
    content = Content.query.get_or_404(content_id)
    
    rating_value = request.form.get('rating', type=int)
    review_text = request.form.get('review', '').strip()
    
    if not rating_value or rating_value < 1 or rating_value > 5:
        flash('Avaliação inválida. Escolha entre 1 e 5 estrelas.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    existing = Rating.query.filter_by(
        user_id=current_user.id,
        content_id=content_id
    ).first()
    
    try:
        if existing:
            existing.rating = rating_value
            existing.review = review_text if review_text else None
            flash('Sua avaliação foi atualizada!', 'success')
        else:
            new_rating = Rating(
                user_id=current_user.id,
                content_id=content_id,
                rating=rating_value,
                review=review_text if review_text else None
            )
            db.session.add(new_rating)
            flash('Avaliação enviada com sucesso!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar avaliação: {str(e)}', 'danger')
    
    return redirect(url_for('content.view_content', content_id=content_id))


@content_bp.route('/rating/<int:rating_id>/remove', methods=['POST'])
@login_required
def remove_rating(rating_id):
    """Remove uma avaliação existente"""
    rating = Rating.query.get_or_404(rating_id)
    content_id = rating.content_id

    # Permissão: autor ou admin
    if current_user.id != rating.user_id and not current_user.is_admin:
        flash('Você não tem permissão para excluir esta avaliação.', 'danger')
        return redirect(url_for('content.view_content', content_id=content_id))
    
    try:
        db.session.delete(rating)
        db.session.commit()
        flash('Avaliação excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir avaliação: {str(e)}', 'danger')
    
    return redirect(url_for('content.view_content', content_id=content_id))
