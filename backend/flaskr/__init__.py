from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection ]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
   

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def retrieve_categories():
        category = Category.query.all()
        categories = [question.format() for question in category ]
        

        return jsonify(
            {
                "success":True,
                "list_categories":categories,
                "total_categories":len(Category.query.all()),
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request,selection)
        if current_questions == 0:
            abort(404)
        return jsonify(
            {
                "success":True,
                "Questions":current_questions,
                "total_questions":len(Question.query.all())
            }
        )
   

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            
            if question is None:
                abort(404)
            
            question.delete()

            selection = Question.query.all()
            current_questions =paginate_questions(request, selection)

            return jsonify(
                {
                    "success":True,
                    "deleted":question_id,
                    "questions":current_questions,
                    "total_questions":len(Question.query.all()),
                }
            )
        
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def post_question():
        body = request.get_json()

        post_question = body.get('question', None)
        post_answer = body.get('answer', None)
        post_difficulty = body.get('difficulty',None)
        post_category = body.get('category', None)

        try:
            question = Question(question=post_question, answer=post_answer, difficulty=post_difficulty, category=post_category)
            question.insert()
            return jsonify({
                'success':True,
                'message':'Question created successfully'
            })

        except:
            abort(422)




    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions", methods=["POST"])
    def search_question():
        body  = request.get_json()
        search =body.get("search", None)
        if search == None:
            abort(400)
        try:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%").fomart(search))
            current_questions =paginate_questions(request, selection)

            return jsonify(
                {
                    "success":True,
                    "questions":current_questions,
                    "total_questions":len(selection.all()),
                }
                         )

        except:
            abort(404)
    


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=['GET'])

    def get_question_by_category(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        
        if (category is None):
            abort(400)
       
        
        try:
            selection = Question.query.filter(Question.category == str(category_id)).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success":True,
                "questions":current_questions,
                "total_questions":len(selection),
                "current_category":category_id

            })


        except:
            abort(422)

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
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        previous_quiz = body.get(previous_quiz)

        category = body.get('quiz_category')


        if (category['id'] == 0):
            questions = Question.query.all()


        else:
            questions = Question.query.filter_by(category=category['id']).all()


        def get_random_question():
            return questions[random.randrange(0, len(questions), -1)]

        upcoming_question = get_random_question

        used = True
        while used:
            if upcoming_question.id in previous_quiz:
                upcoming_question = get_random_question
            else:
                used = False

                return jsonify({
                    "success": True,
                    "question":upcoming_question.format()
                })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({
                         "success":False,
                         "error":404,
                         "message":"resource not found"
                         }), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify ({
                    "success":False,
                    "error":422,
                    "message": "unprocessable"
                }), 422)

    @app.errorhandler(400)
    def bad_request(error):
        return(jsonify({
                    "success":False,
                    "error":400,
                    "message":"Bad Request"
                }), 400)







    return app

