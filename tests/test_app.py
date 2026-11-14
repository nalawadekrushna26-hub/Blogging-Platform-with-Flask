"""
Comprehensive Automated Test Suite for Blogging Platform.
Uses Python unittest with in-memory SQLite database (TestingConfig).
Tests: Models, Authentication, Blog CRUD, Comments, Search, and Security Headers.
"""

import unittest
from app import create_app, db
from app.models import User, Post, Category, Tag, Comment
from config import TestingConfig


class BlogPlatformTestCase(unittest.TestCase):
    """Test suite covering the full blogging platform lifecycle."""

    def setUp(self):
        """Set up an isolated in-memory test environment before each test."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create fresh database tables
        db.create_all()

        # Seed test category
        self.category = Category(name="Tech", slug="tech", description="Tech articles")
        db.session.add(self.category)

        # Seed test author
        self.author = User(username="alice", email="alice@example.com")
        self.author.set_password("Password123!")
        db.session.add(self.author)

        # Seed second user
        self.reader = User(username="bob", email="bob@example.com")
        self.reader.set_password("Password123!")
        db.session.add(self.reader)

        db.session.commit()

    def tearDown(self):
        """Clean up database session and drop tables after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==========================================
    # 1. Model Tests
    # ==========================================
    def test_password_hashing(self):
        """Verify passwords are never stored in plain text and hashes verify correctly."""
        user = User(username="charlie", email="charlie@example.com")
        user.set_password("Secret123")
        self.assertNotEqual(user.password_hash, "Secret123")
        self.assertTrue(user.check_password("Secret123"))
        self.assertFalse(user.check_password("WrongPassword"))

    def test_slug_generation(self):
        """Verify URL slug generator creates valid, URL-safe slugs."""
        slug = Post.generate_slug("Building a Flask Platform in 2026!")
        self.assertEqual(slug, "building-a-flask-platform-in-2026")

    # ==========================================
    # 2. Authentication Route Tests
    # ==========================================
    def test_user_registration(self):
        """Verify registration works and rejects duplicate usernames/emails."""
        res = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Your account has been created successfully', res.data)

        # Duplicate email test
        res_dup = self.client.post('/auth/register', data={
            'username': 'otheruser',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)
        self.assertIn(b'An account with this email already exists', res_dup.data)

    def test_user_login_and_logout(self):
        """Verify login with valid/invalid credentials and logout."""
        # Invalid password
        res_bad = self.client.post('/auth/login', data={
            'email': 'alice@example.com',
            'password': 'BadPassword'
        }, follow_redirects=True)
        self.assertIn(b'Login unsuccessful', res_bad.data)

        # Valid login
        res_good = self.client.post('/auth/login', data={
            'email': 'alice@example.com',
            'password': 'Password123!'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, alice!', res_good.data)

        # Logout
        res_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out successfully', res_logout.data)

    # ==========================================
    # 3. Blog Post CRUD Tests
    # ==========================================
    def test_post_creation_and_view(self):
        """Verify authenticated users can publish posts and view them."""
        # Login
        self.client.post('/auth/login', data={'email': 'alice@example.com', 'password': 'Password123!'})

        # Create post
        res_create = self.client.post('/posts/create', data={
            'title': 'Test Article on Flask',
            'summary': 'Short description of test article',
            'content': '<p>This is rich content from Quill editor.</p>',
            'category': self.category.id,
            'tags': 'flask, python, testing',
            'is_published': 'y'
        }, follow_redirects=True)
        self.assertEqual(res_create.status_code, 200)
        self.assertIn(b'Test Article on Flask', res_create.data)

        # Verify database record & slug
        post = Post.query.filter_by(slug='test-article-on-flask').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author.username, 'alice')
        self.assertEqual(len(post.tags), 3)

        # View post detail
        res_view = self.client.get(f'/posts/{post.slug}')
        self.assertEqual(res_view.status_code, 200)
        self.assertIn(b'This is rich content from Quill editor', res_view.data)

    def test_post_edit_and_delete(self):
        """Verify authors can update and delete their own posts."""
        self.client.post('/auth/login', data={'email': 'alice@example.com', 'password': 'Password123!'})

        post = Post(
            title="Initial Title",
            slug="initial-title",
            content="Initial Content",
            category_id=self.category.id,
            author=self.author,
            is_published=True
        )
        db.session.add(post)
        db.session.commit()

        # Update post
        res_edit = self.client.post(f'/posts/{post.id}/edit', data={
            'title': 'Updated Title',
            'content': 'Updated Content',
            'category': self.category.id,
            'tags': 'updated',
            'is_published': 'y'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn(b'Your article has been updated successfully!', res_edit.data)

        # Delete post
        res_del = self.client.post(f'/posts/{post.id}/delete', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)
        self.assertIn(b'Your article has been permanently deleted', res_del.data)
        self.assertIsNone(db.session.get(Post, post.id))

    # ==========================================
    # 4. Comments Tests
    # ==========================================
    def test_comment_lifecycle(self):
        """Verify readers can comment and authors can delete comments."""
        post = Post(
            title="Discussion Article",
            slug="discussion-article",
            content="Body text",
            category_id=self.category.id,
            author=self.author,
            is_published=True
        )
        db.session.add(post)
        db.session.commit()

        # Login as reader
        self.client.post('/auth/login', data={'email': 'bob@example.com', 'password': 'Password123!'})

        # Add comment
        res_comment = self.client.post(f'/posts/{post.slug}/comment', data={
            'content': 'Insightful article, thanks for sharing!'
        }, follow_redirects=True)
        self.assertEqual(res_comment.status_code, 200)
        self.assertIn(b'Insightful article, thanks for sharing!', res_comment.data)

        comment = Comment.query.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.author.username, 'bob')

        # Delete comment
        res_del_comment = self.client.post(f'/posts/comment/{comment.id}/delete', follow_redirects=True)
        self.assertEqual(res_del_comment.status_code, 200)
        self.assertIsNone(db.session.get(Comment, comment.id))

    # ==========================================
    # 5. Search & Filter Tests
    # ==========================================
    def test_multi_field_search(self):
        """Verify search query matches title, summary, or content."""
        post1 = Post(title="Deep Learning with PyTorch", slug="dl-pytorch", content="Neural nets", category_id=self.category.id, author=self.author, is_published=True)
        post2 = Post(title="Web Design Principles", slug="web-design", content="Color palettes and CSS", category_id=self.category.id, author=self.author, is_published=True)
        db.session.add_all([post1, post2])
        db.session.commit()

        # Search for 'pytorch'
        res = self.client.get('/search?q=pytorch')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Deep Learning with PyTorch', res.data)
        self.assertNotIn(b'Web Design Principles', res.data)

    # ==========================================
    # 6. Security Headers & Error Handlers Tests
    # ==========================================
    def test_security_headers_and_404(self):
        """Verify custom 404 page and presence of security headers."""
        res_404 = self.client.get('/nonexistent-page-url')
        self.assertEqual(res_404.status_code, 404)
        self.assertIn(b'Page not found', res_404.data)

        # Check Security Headers
        self.assertEqual(res_404.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(res_404.headers.get('X-Content-Type-Options'), 'nosniff')


if __name__ == '__main__':
    unittest.main()
