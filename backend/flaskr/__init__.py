from hashlib import new
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
import collections
collections.Iterable = collections.abc.Iterable


# declaring global variable
QUESTIONS_PER_PAGE = 10

# Helper method:


def paginated_question(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_question = [item.format() for item in selection]
    current_questions = formatted_question[start:end]

    return current_questions


def create_app(test_config=None):
    # creating and configuring my app
    app = Flask(__name__)
    setup_db(app)

    # CORS Set up that Allows '*' for origins.
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_resquest(response):
        response.headers.add("Access-Allow-Headers",
                             "Content-Type,Authentication,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # Endpoint to handle GET requests for all acategories.

    @app.route('/categories')
    def retrieve_categories():
        get_categories = Category.query.order_by(Category.id).all()

        if len(get_categories) == 0:
            abort(404)

        try:
            result = {cat.id: cat.type for cat in get_categories}
            return ({
                'success': True,
                'categories': result,
                'total_categories': len(result)
            })

        except Exception:
            abort(422)

    # An endpoint to handle GET requests for questions
    # This endpoint should return a list of questions
    # number of total questions, current category, categories.

    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()

        questions = paginated_question(request, selection)

        if len(questions) == 0:
            abort(404)

        try:
            categories_list = {cat.id: cat.type for cat in categories}

            return jsonify({
                'success': True,
                'questions': list(questions),
                'total_questions': len(selection),
                'current_category': None,
                'categories': categories_list
            })

        except Exception:
            abort(422)

    # Creating an endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Quering the Question model to filter based on the ID
        question = Question.query.filter_by(id=question_id).one_or_none()

        if question is None:
            abort(404)

        try:
            question.delete()
            # Total number of questions remaining
            total_questions = len(Question.query.all())

            return ({
                'success': True,
                'deleted_question_id': question_id,
                'total_questions': total_questions
            })

        except Exception:
            abort(422)

    """
    An endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        questions = Question.query.order_by(Question.id).all()
        body = request.get_json()

        # getting the input fields from form
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        # throw error if none of these fields have value
        if (body, new_category, new_question,
                new_answer, new_difficulty) is None:
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )

            # Insert into Question model is everything is fine
            question.insert()

            return jsonify({
                'success': True,
                'created_question': question.id,
                'questions': paginated_question(request, questions),
                'total_questions': len(questions)
            })

        except Exception:
            abort(422)

    # Sample Request:
    """
    curl -X POST -H "Content-Type: application/json"
    -d '{"question":"what is my country?", "answer":"Nigeria",
    "category":"5", "difficulty":"2"}'
    http://127.0.0.1:5000/questions
    """

    """
    A POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.args.get('search')
        selection = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

        search_questions = paginated_question(request, selection)

        if search_term is None:
            abort(404)

        return jsonify({
            "success": True,
            "questions": list(search_questions),
            "total_questions": len(selection),
        })

    """
    Creating a GET endpoint to get questions based on category.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        categories = Category.query.all()

        try:
            selection = Question.query.filter(
                category_id == Question.category).all()

            current_questions = paginated_question(request, selection)

            # throw error if the entered category_id is greater
            if category_id > len(categories):
                abort(404)
            # Returning message body
            return jsonify({
                "success": True,
                "questions": list(current_questions),
                "total_questions": len(selection),
                "current_category": [cat.type for cat in
                                     categories if cat.id == category_id]
            })

        except Exception:
            abort(404)
        # Sample request:
        # http://127.0.0.1:5000/categories/3/questions

    """
    Creating a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def start_trivia():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_category['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions),
                                                  Question.category == category_id).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions),
                                                  Question.category == category_id).all()

            question = None
            if (questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except Exception:
            abort(422)
    """
    Creating necessary error handlers for all expected errors
    """
    # Request cannot be processed
    @app.errorhandler(422)
    def unprocesseable(error):
        return (
            jsonify({
                'success': False,
                'error': 422,
                'message': 'request cannot be processed'
            }), 422

        )

    # Resource not found Error
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                'success': False,
                'error': 404,
                'message': 'resource not found'
            }), 404
        )

    # Bad request
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                'error': 400,
                'message': 'bad request'
            }), 400

        )

    # method not alllowed
    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({
                'success': False,
                'error': 405,
                'message': 'method not allowed'
            }), 405
        )

    return app
