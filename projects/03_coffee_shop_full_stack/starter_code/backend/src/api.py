import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES
'''
Route handler for display existing drinks.
'''
@app.route('/drinks')
def get_drinks():
    # get all drinks
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .short()
    drinks_short = [drink.short() for drink in drinks]

    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


'''
Route handler for get drink-details.
Requires 'get:drinks-details' permission.
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)
    drinks_long = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks_long
    })


'''
Route handler for create a new drink.
Requires 'post:drinks' permission.
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    # get the drink info from request
    body = request.get_json()
    title = body['title']
    recipe = body['recipe']

    # create new drink
    drink = Drink(title=title, recipe=json.dumps(recipe))

    try:
        # add drink to database
        drink.insert()
    except Exception as e:
        print('ERROR', str(e))
        abort(422)

    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


'''
Route handler for editing existing drink.
Requires 'patch:drinks' permission.
'''
@app.route('/drinks', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks_by_id(*args, **kwargs):
    #get ID from the kwargs
    id = kwargs['id']

    #get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    # get request body
    body = request.get_json()

    #update title if present in body
    if 'title' in body:
        drink.title = body['title']

    #Update recipe if present in body
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    try:
        #update drink in database
        drink.insert()

    except Exception as e:
        # catch exception
        print('EXCEPTION: ', str(e))

        # Bad request
        abort(400)

    # Array containing .long representation
    drink = [drink.long()]

    # return drink to view
    return jsonify({
        'success': True,
        'drinks': drink
    })

'''
Route handler for delete existing drink.
Requires 'delete:drinks' permission.
'''
@app.route('/drinks', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(*args, **kwargs):
    # get ID from kwargs
    id = kwargs['id']

    #get drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
    except Exception as e:
        print('EXCEPTION: ', str(e))

        abort(500)

    # return status and deleted drink id
    return jsonify({
        'success': True,
        'delete': id
    })

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
Error handler for resource not found
'''
@app.errorhandler(404)
def resouce_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
Error handler for bad request
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "resource not found"
    }), 400


'''
Error handling for AuthError
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
