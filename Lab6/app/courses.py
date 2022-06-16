from cgitb import text
from flask import Blueprint, redirect, render_template, request, flash, url_for
from flask_login import current_user
from app import db
from models import Course, Category, Review, User
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

PER_PAGE = 3

COURSE_PARAMS = ['author_id', 'name', 'category_id', 'short_desc', 'full_desc']

def params():
    return {p: request.form.get(p) for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': request.args.getlist('category_ids')
    }

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    courses = CoursesFilter(**search_params()).perform()
    pagination = courses.paginate(page, PER_PAGE)
    courses = pagination.items

    categories = Category.query.all()

    return render_template('courses/index.html', 
                            courses=courses, 
                            categories=categories,
                            pagination=pagination,
                            search_params=search_params()
                            )
                            
@bp.route('/new')
def new():
    categories = Category.query.all()
    users = User.query.all()
    return render_template('courses/new.html', 
                            categories=categories, 
                            users=users
                            )

@bp.route('/create', methods=["POST"])
def create():

    f = request.files.get('background_img') or None
    if f and f.filename:
        img = ImageSaver(f).save()

    course = Course(**params(), background_image_id = img.id)
    db.session.add(course)
    db.session.commit()

    flash(f'Курс {course.name} был успешно создан.')
    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.created_at.desc()).limit(5).all()
    course = Course.query.get(course_id)

    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter(Review.course_id == course_id).filter(Review.user_id == current_user.id).first()

    return render_template('courses/show.html', course=course, reviews=reviews, user_review=user_review)

@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('filters')
    reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.created_at.desc())

    if sort_type == 'new': reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.created_at.desc())
    if sort_type == 'old': reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.created_at.asc())
    if sort_type == 'positive': reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.rating.desc())
    if sort_type == 'negative': reviews = Review.query.filter(Review.course_id == course_id).order_by(Review.rating.asc())

    pagination = reviews.paginate(page, PER_PAGE)
    reviews = reviews.paginate(page, PER_PAGE).items

    return render_template('courses/reviews.html', reviews=reviews, pagination=pagination)


@bp.route('/<int:course_id>/reviews/create', methods=["POST"])
def create_review(course_id):
    user_id = current_user.id
    review_rating = request.form.get('review-rating')
    review_text = request.form.get('review-text')
    user_review = Review(user_id=user_id, rating=review_rating, text=review_text, course_id=course_id)
    db.session.add(user_review)
    course = Course.query.get(course_id)
    course.rating_sum += int(review_rating)
    course.rating_num += 1
    db.session.commit()
    return redirect(url_for('courses.index'))
