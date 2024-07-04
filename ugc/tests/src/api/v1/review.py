import sys
from unittest.mock import patch

import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from http import HTTPStatus

sys.path.append("ugc/api/src/")
from main import db, ugc_blueprint
from models.review import Review


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test_secret"
    db.init_app(app)
    app.register_blueprint(ugc_blueprint)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def access_token(app):
    with app.app_context():
        return create_access_token(identity=1)


@patch("models.review.db.session")
def test_add_review(mock_session, client, access_token):
    review_data = {"content": "Great movie!", "rating": 5}

    response = client.post(
        "/ugc/api/v1/123/review",
        json=review_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert mock_session.add.called
    assert mock_session.commit.called


# Тест для получения отзывов
@patch("models.review.Review.query")
def test_retrieve_reviews(mock_query, client, access_token):
    mock_query.filter_by.return_value.all.return_value = [
        Review(movie_id=123, user_id=1, content="Great movie!", rating=5)
    ]

    response = client.get("/ugc/api/v1/123/review", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json == [{"movie_id": 123, "user_id": 1, "content": "Great movie!", "rating": 5}]


@patch("models.review.Review.query")
@patch("models.review.db.session")
def test_delete_review(mock_session, mock_query, client, access_token):
    review_data = {"content": "Great movie!", "rating": 5}
    mock_query.filter_by.return_value.first.return_value = Review(
        movie_id=123, user_id=1, content="Great movie!", rating=5
    )

    response = client.delete(
        "/ugc/api/v1/123/review",
        json=review_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert mock_session.delete.called
    assert mock_session.commit.called
