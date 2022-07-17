import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@requires_auth("get:drinks")
def get_drinks(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formated_drinks = [drink.short() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": formated_drinks
        })
    except:
        db.session.rollback()
        abort(404)
    finally:
        db.session.close()

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):

    try:
        drinks = Drink.query.order_by(Drink.id).all()
        long_format_drinks_detail = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": long_format_drinks_detail
        })

    except:
        db.session.rollback()
        abort(404)

    finally:
        db.session.close()

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    recipe = body.get("recipe", None)
    title = body.get("title", None)

    if recipe is None:
        abort(400, "recipe was not provided")
    if title is None or title == "":
        abort(400, "title was not provided")
    recipe = json.dumps(recipe)

    drink = None
    try:
        drink_db = Drink(recipe=recipe, title=title)
        drink_db.insert()
        drink = [drink_db.long()]
    except:
        print(sys.exc_info())
        abort(500)
        
    return jsonify({
        "success": True,
        "drinks": drink
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    recipe = body.get("recipe", None)
    title = body.get("title", None)

    if recipe is None:
        abort(400, "recipe was not provided")
    if title is None or title == "":
        abort(400, "title was not provided")
    recipe = json.dumps(recipe)

    drink_db = Drink.query.get(id)
    if drink_db is None:
        abort(404, "Drink not found")

    drink = None
    try:
        drink_db.recipe = recipe
        drink_db.title = title
        drink_db.update()
        drink = [drink_db.long()]
    except:
        print(sys.exc_info())
        abort(500)
        
    return jsonify({
        "success": True,
        "drinks": drink
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink_db = Drink.query.get(id)
    if drink_db is None:
        abort(404, "Drink not found")

    try:
        drink_db.delete()
    except:
        print(sys.exc_info())
        abort(500)
        
    return jsonify({
        "success": True,
        "drinks": id
    }), 200

# Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
# error handler for bad request (400)
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

# error handler for unauthorized (401)
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

# error handler for forbidden (403)
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
# error handler for resource not found (404)
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

#errorhandler for internal server error (500)
@app.errorhandler(500)
def internal_server_error(error):
    print({"error": error})
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# error handler for AuthError
@app.errorhandler(AuthError)
def internal_auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error['description']
    }), auth_error.status_code
