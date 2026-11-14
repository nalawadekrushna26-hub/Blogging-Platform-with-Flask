"""
Flask-WTF Forms for Blog Post Management.
Supports title, summary, Quill.js rich HTML content, category selection,
comma-separated tags, featured image upload, and draft/publish toggling.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    """Form for creating and editing blog posts."""
    title = StringField(
        'Article Title',
        validators=[DataRequired(), Length(min=5, max=150, message='Title must be between 5 and 150 characters.')]
    )
    summary = TextAreaField(
        'Short Summary / Subtitle',
        validators=[Optional(), Length(max=300, message='Summary cannot exceed 300 characters.')]
    )
    # HiddenField receives the formatted HTML from Quill.js editor on form submit
    content = HiddenField(
        'Content',
        validators=[DataRequired(message='Article content cannot be empty.')]
    )
    category = SelectField(
        'Category',
        coerce=int,
        validators=[DataRequired(message='Please choose a category.')]
    )
    tags = StringField(
        'Tags (comma-separated)',
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "e.g. python, flask, webdev"}
    )
    featured_image = FileField(
        'Featured Cover Image',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)!')]
    )
    is_published = BooleanField('Publish immediately (leave unchecked to save as Draft)', default=True)
    submit = SubmitField('Publish Story')



class CommentForm(FlaskForm):
    """Form for readers to submit comments under articles."""
    content = TextAreaField(
        'Leave a Comment',
        validators=[
            DataRequired(message='Comment cannot be empty.'),
            Length(min=2, max=1000, message='Comment must be between 2 and 1000 characters.')
        ],
        render_kw={"rows": 3, "placeholder": "Share your thoughts or ask a question..."}
    )
    submit = SubmitField('Submit Comment')
