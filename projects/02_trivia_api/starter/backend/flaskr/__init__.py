from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_cors import CORS
from sqlalchemy import func

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

    @app.route('/categories')
    def get_categories():
        category_list = Category.query.with_entities(Category.type).all()

        if len(category_list) == 0:
            abort(404)

        return jsonify({
            'categories': category_list
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
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True
            })
        except:
            abort(405)

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

        if not id:
            return abort(400, 'Invalid category id')

        selection = Question.query.filter(Question.category == id).all()
        questions = paginate_categories(request, selection)

        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': Category.query.with_entities(Category.type).filter(id == id).all()[0]
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')
        category_id = int(category.get('id'))
        questions = Question.query.filter(Question.category == category_id)
        question = questions.order_by(func.random()).first()
        return jsonify({
            'question': question.format()
        })

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
