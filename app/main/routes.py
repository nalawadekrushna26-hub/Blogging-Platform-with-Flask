"""
Main routes for general site navigation, home page, dashboard, search, and tag filtering.
"""

from flask import render_template, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.main import main_bp
from app.models import Post, Category, Tag, Comment


@main_bp.route('/')
def index():
    """
    Modern homepage route displaying:
    - Optional category filter
    - Prominent featured hero story (latest article)
    - Grid of recent articles
    - Live category pills
    """
    selected_category_slug = request.args.get('category')
    categories = Category.query.order_by(Category.name).all()

    query = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc())

    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    all_matching_posts = query.all()

    # Feature first post when on default un-filtered homepage
    featured_post = None
    recent_posts = all_matching_posts
    if not selected_category_slug and all_matching_posts:
        featured_post = all_matching_posts[0]
        recent_posts = all_matching_posts[1:]

    return render_template(
        'main/index.html',
        featured_post=featured_post,
        posts=recent_posts,
        categories=categories,
        selected_category=selected_category,
        total_count=len(all_matching_posts)
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Author analytics dashboard displaying publication statistics and article management."""
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()

    # Calculate key metrics
    total_posts = len(user_posts)
    published_count = sum(1 for p in user_posts if p.is_published)
    draft_count = total_posts - published_count

    # Aggregate reader comments across all author's articles
    post_ids = [p.id for p in user_posts]
    total_comments = Comment.query.filter(Comment.post_id.in_(post_ids)).count() if post_ids else 0

    return render_template(
        'main/dashboard.html',
        posts=user_posts,
        total_posts=total_posts,
        published_count=published_count,
        draft_count=draft_count,
        total_comments=total_comments
    )


@main_bp.route('/search')
def search():
    """
    Global multi-field search engine.
    Matches search keywords against Post title, summary, and rich content.
    """
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 6)

    posts_pagination = None
    total_results = 0

    if query:
        search_filter = or_(
            Post.title.ilike(f'%{query}%'),
            Post.summary.ilike(f'%{query}%'),
            Post.content.ilike(f'%{query}%')
        )
        posts_pagination = Post.query.filter_by(is_published=True)\
            .filter(search_filter)\
            .order_by(Post.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        total_results = posts_pagination.total

    categories = Category.query.order_by(Category.name).all()
    return render_template(
        'main/search.html',
        query=query,
        pagination=posts_pagination,
        total_results=total_results,
        categories=categories
    )


@main_bp.route('/tag/<string:slug>')
def tag_posts(slug):
    """Filter and display all published articles associated with a specific tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 6)

    posts_pagination = tag.posts.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.order_by(Category.name).all()
    return render_template(
        'main/search.html',
        tag=tag,
        query=f"#{tag.name}",
        pagination=posts_pagination,
        total_results=posts_pagination.total,
        categories=categories
    )
