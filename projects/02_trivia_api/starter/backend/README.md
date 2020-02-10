# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API Documentation

GET "/categories"

Fetches the categories
Request Parameters: None
Response Body:
categories: Dictionary of Category ID <-> Category Type

{
  "categories": {
    "1": "Science",
    "2": "Art"
  } 
}

GET "/questions?page=1"

Fetches the questions to be displayed on the page using page number
Request Parameters: page: Page number
Response Body:
questions: List of questions

categories: Dictionary of Category ID <-> Category Type

total_questions: Total number of questions

{
  "questions": [{
    "id": 1,
    "question": "",
    "answer": "",
    "category": 1,
    "difficulty": 1
  }],
  "categories": {
    "1": "Science",
    "2": "Art"
  },
  "total_questions": 1
}

DELETE "/questions/int:question_id"

Deletes a question from the database
Request Parameters: question_id: Question ID to delete
Response Body:
deleted: Question ID that is deleted

{
  "deleted": 20
}

POST "/questions"

Adds a questions to the database
Request Body:
question: Question statement

answer: Answer statement

category: Category ID

difficulty: Difficulty Level

Response Body:
question: Question object that is created

{
  "question": {
    "id": 1,
    "question": "",
    "answer": "",
    "category": 1,
    "difficulty": 1
  }
}

POST "/search"

Fetches questions based on the search term
Request Body:
searchTerm: Search term

Response Body:
questions: List of questions found in search

total_questions: Total number of questions

{
  "questions": [{
    "id": 1,
    "question": "",
    "answer": "",
    "category": 1,
    "difficulty": 1
  }],
  "total_questions": 1
}

GET "/categories/int:category_id/questions"

Fetches questions for the requested category
Request Parameters: category_id: Category ID for questions
Response Body:
questions: List of category questions

total_questions: Total number of questions

current_category: Current category ID

{
  "questions": [{
    "id": 1,
    "question": "",
    "answer": "",
    "category": 1,
    "difficulty": 1
  }],
  "total_questions": 1,
  "current_category": 1
}

POST "/quizzes"

Fetches a unique question for the quiz on selected category
Request Body:
previous_questions: List of previously answered questions

quiz_category: Category object of the quiz

Response Body:
question: Random question of requested category

{
  "question": {
    "id": 1,
    "question": "",
    "answer": "",
    "category": 1,
    "difficulty": 1
  }
}

```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
