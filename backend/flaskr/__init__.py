import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
import collections
collections.Iterable = collections.abc.Iterable

QUESTIONS_PER_PAGE = 10

# Helper method:
def paginated_question(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    formatted_question = [item.format() for item in selection]
    current_questions = formatted_question[start:end]

    return current_questions

    if(len(formatted_question) < start):
        abort(400)



def create_app(test_config=None):
    # creating and configuring my app
    app = Flask(__name__)
    setup_db(app)
    
    # CORS Set up that Allows '*' for origins.
    collections.Callable = collections.abc.Callable
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_resquest(response):
        response.headers.add("Access-Allow-Headers", "Content-Type,Authentication,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
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
            return({
                'success': True,
                'categories': result,
                'total_categories': len(result)
            })
        
        except:
            abort(422)


    # An endpoint to handle GET requests for questions
    # This endpoint should return a list of questions, number of total questions, current category, categories.
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

        except:
            abort(422)
    
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

