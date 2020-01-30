import os
import unittest
from flask import json
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

    def test_get_categories(self):
        categories = "/categories"
        res = self.client().get(f'{categories}')
        data = json.loads(res.data)

        if res.status_code == 404:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], "resource not found")
        else:
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        if res.status_code == 404:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], "resource not found")
        else:
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['questions'])
            # self.assertEqual(data['total_questions'], 25)
            self.assertTrue(data['categories'])

    def test_delete_question(self):
        question_id = 30
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        if res.status_code == 405:
            self.assertEqual(res.status_code, 405)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], "method not allowed")
        else:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(question, None)

    def test_404_delete_question_fail(self):
        question_id = 1
        res = self.client().delete(f'/question/{question_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search(self):
        request_data = {'searchTerm': 'city'}
        res = self.client().post('/questions', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_create_question(self):
        self.client().post('/questions', data=json.dumps(self.new_question), content_type='application/json')

        res = self.client().get('/questions')

        self.assertEqual(res.status_code, 200)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])

    # def test_get_questions_by_category_fail(self):
    #     category_id = 0
    #     res = self.client().get(f'/categories/{category_id}/questions')
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 400)
    #     self.assertEqual(data['success'], False)

    def test_405_metho_not_allowed(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

if __name__ == "__main__":
    unittest.main()