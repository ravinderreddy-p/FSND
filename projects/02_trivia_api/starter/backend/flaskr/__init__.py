from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_cors import CORS
from flask_restful.representations import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,True')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response

    @app.route('/')
    def index():
        questions_list = Question.query.all()
        questions = paginate_categories(request, questions_list)

        if len(questions) == 0:
            abs(404)
        return jsonify({
            'questions': questions
        })

    @app.route('/categories')
    def get_categories():
        category_list = Category.query.all()
        categories = paginate_categories(request, category_list)

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'categories': categories
        })

    @app.route('/questions', methods=["GET"])
    def get_questions():
        questions_list = Question.query.all()
        questions = paginate_categories(request, questions_list)
        categories = Category.query.all()
        categories_list = [category.type for category in categories]

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'status': 200,
            'questions': questions,
            'total_questions': len(Question.query.all()),
            'categories': categories_list
            # 'current_category': 'All'
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            'success': True
        })

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        search = body.get('searchTerm', None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                search_questions = paginate_categories(request, selection)

                return jsonify({
                    'success': True,
                    'questions': search_questions
                })
            else:
                question = Question(question=new_question, answer=new_answer, category=new_category,
                                    difficulty=new_difficulty)
                question.insert()

                return redirect(url_for('get_questions'))
        except:
            abort(405)

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        selection = Question.query.filter(Question.category == id).all()
        questions = paginate_categories(request, selection)

        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': Category.query.with_entities(Category.type).filter(id == id).all()[0]
        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
