"""
Posts routes for creating, listing, viewing, updating, and deleting blog posts,
as well as managing reader discussions (comments).
"""

import secrets
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app.posts import posts_bp
from app.posts.forms import PostForm, CommentForm
from app.extensions import db
from app.models import Post, Category, Tag, Comment
from app.utils import save_image


def sync_tags(tag_names_str):
    """Parse comma-separated tag string into a list of Tag model instances."""
    tags = []
    if not tag_names_str:
        return tags

    raw_tags = [t.strip().lower() for t in tag_names_str.split(',') if t.strip()]
    unique_tags = list(dict.fromkeys(raw_tags))

    for tag_name in unique_tags:
        slug = Post.generate_slug(tag_name)
        tag = Tag.query.filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=tag_name, slug=slug)
            db.session.add(tag)
        tags.append(tag)
    return tags


@posts_bp.route('/')
def list_posts():
    """Display paginated list of all published blog posts."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 6)

    posts_pagination = Post.query.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.order_by(Category.name).all()
    return render_template('posts/list_posts.html', pagination=posts_pagination, categories=categories)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create and publish a new blog post."""
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        base_slug = Post.generate_slug(form.title.data)
        slug = base_slug
        if Post.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{secrets.token_hex(3)}"

        featured_image = None
        if form.featured_image.data:
            featured_image = save_image(form.featured_image.data)

        tags = sync_tags(form.tags.data)

        post = Post(
            title=form.title.data.strip(),
            slug=slug,
            summary=form.summary.data.strip() if form.summary.data else None,
            content=form.content.data,
            category_id=form.category.data,
            featured_image=featured_image,
            is_published=form.is_published.data,
            author=current_user,
            tags=tags
        )
        db.session.add(post)
        db.session.commit()

        status_msg = "published" if post.is_published else "saved as draft"
        flash(f'Your article has been {status_msg} successfully!', 'success')
        return redirect(url_for('posts.view_post', slug=post.slug))

    return render_template('posts/create_post.html', form=form, title="Create New Post")


@posts_bp.route('/<string:slug>')
def view_post(slug):
    """View a single blog post and its discussion comments."""
    post = Post.query.filter_by(slug=slug).first_or_404()

    # Draft protection: only the author can view drafts
    if not post.is_published and (not current_user.is_authenticated or current_user.id != post.user_id):
        abort(404)

    comment_form = CommentForm()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    return render_template(
        'posts/post_detail.html',
        post=post,
        comments=comments,
        comment_form=comment_form
    )


@posts_bp.route('/<string:slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    """Add a new comment under a blog article."""
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data.strip(),
            author=current_user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added to the discussion!', 'success')
    else:
        for error in form.content.errors:
            flash(error, 'danger')

    return redirect(url_for('posts.view_post', slug=post.slug) + '#comments-section')


@posts_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (Comment author or Post author only)."""
    comment = Comment.query.get_or_404(comment_id)
    post_slug = comment.post.slug

    # Authorization Check: only the author of the comment or the owner of the article can delete it
    if comment.author != current_user and comment.post.author != current_user:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('posts.view_post', slug=post_slug) + '#comments-section')

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'info')
    return redirect(url_for('posts.view_post', slug=post_slug) + '#comments-section')


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit an existing blog post (Author only)."""
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        flash("You are not authorized to edit this article.", "danger")
        return redirect(url_for('posts.view_post', slug=post.slug))

    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]

    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.summary = form.summary.data.strip() if form.summary.data else None
        post.content = form.content.data
        post.category_id = form.category.data
        post.is_published = form.is_published.data

        if form.featured_image.data:
            post.featured_image = save_image(form.featured_image.data)

        post.tags = sync_tags(form.tags.data)

        db.session.commit()
        flash('Your article has been updated successfully!', 'success')
        return redirect(url_for('posts.view_post', slug=post.slug))

    elif request.method == 'GET':
        form.title.data = post.title
        form.summary.data = post.summary
        form.content.data = post.content
        form.category.data = post.category_id
        form.is_published.data = post.is_published
        form.tags.data = ', '.join([t.name for t in post.tags])

    return render_template('posts/edit_post.html', form=form, post=post, title="Edit Post")


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a blog post and its associated comments (Author only)."""
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        flash("You are not authorized to delete this article.", "danger")
        return redirect(url_for('posts.view_post', slug=post.slug))

    db.session.delete(post)
    db.session.commit()
    flash('Your article has been permanently deleted.', 'info')
    return redirect(url_for('auth.profile'))
