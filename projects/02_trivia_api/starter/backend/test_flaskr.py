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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Which is the capital city of UK',
            'answer': 'London',
            'category': 3,
            'difficulty': 6
        }

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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get("/")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    # def test_get_questions(self):
    #     res = self.client().get("/questions")
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data['questions'])
    #     self.assertEqual(data['total_questions'], 18)
    #     self.assertTrue(data['categories'])
    #
    # def test_delete_question(self):
    #     res = self.client().delete("/questions/5")
    #     data = json.loads(res.data)
    #
    #     question = Question.query.filter(Question.id == 5).one_or_none()
    #
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(question, None)

    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    # def test_404_resource_not_found(self):
    #     res = self.client().post("/questions/1")
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], "resource not found")

    # def test_422_unprocessable(self):
    #     res = self.client().delete('/questions/1000')
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'Unprocessable')

    # def test_405_if_unable_to_add_question(self):
    #     res = self.client().post('/questions/45', json=self.new_question)
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 405)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()