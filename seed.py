"""
Database Seeding Script.
Initializes default categories and tags for the Blogging Platform.
"""

from app import create_app, db
from app.models import Category, Tag

DEFAULT_CATEGORIES = [
    {"name": "Technology", "slug": "technology", "description": "Latest tech trends, gadgets, and software."},
    {"name": "Web Development", "slug": "web-development", "description": "Frontend, backend, APIs, and modern frameworks."},
    {"name": "Python & Flask", "slug": "python-flask", "description": "Python tutorials, Flask architecture, and best practices."},
    {"name": "Design & UI/UX", "slug": "design-ui-ux", "description": "Modern web aesthetics, typography, and user experience."},
    {"name": "Career & Learning", "slug": "career-learning", "description": "Internship tips, engineering roadmaps, and advice."}
]

DEFAULT_TAGS = [
    {"name": "python", "slug": "python"},
    {"name": "flask", "slug": "flask"},
    {"name": "sqlite", "slug": "sqlite"},
    {"name": "webdev", "slug": "webdev"},
    {"name": "javascript", "slug": "javascript"},
    {"name": "tutorial", "slug": "tutorial"}
]


def seed_database():
    """Populate initial categories and tags if not already present."""
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Seed categories
        cat_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            existing = Category.query.filter_by(slug=cat_data["slug"]).first()
            if not existing:
                cat = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"]
                )
                db.session.add(cat)
                cat_count += 1

        # Seed tags
        tag_count = 0
        for tag_data in DEFAULT_TAGS:
            existing = Tag.query.filter_by(slug=tag_data["slug"]).first()
            if not existing:
                tag = Tag(name=tag_data["name"], slug=tag_data["slug"])
                db.session.add(tag)
                tag_count += 1

        db.session.commit()
        print(f"Successfully seeded: {cat_count} categories and {tag_count} tags!")


if __name__ == '__main__':
    seed_database()
