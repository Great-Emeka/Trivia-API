import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "postgres", "localhost:5432", self.database_name
        )
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # Data for testing creation of new question
        self.new_question = {"question":"what is my name", "answer":"Stephen Nwankwo", "category":"5", "difficulty":"2"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Testing for successful operations and for expected errors.
    """
    # Get pages test
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertFalse(data['current_category'])
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_beyond_valid_pages(self):
        res = self.client().get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")


    # Delete a specific question from each request
    def test_delete_question(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 12).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question_id'], 12)
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)

    def test_404_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    #Create New question test:
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['created_question'])
        self.assertTrue(data['total_questions'])

    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post("/questions/41", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


    # Search result test
    def test_get_question__with_search_results(self):
        res = self.client().post('/questions', json={"search": "What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_get_search_unavailable_question(self):
        res = self.client().post('/questions/search', json={"search": "what"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()