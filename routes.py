import logging
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, abort, request
from jwt import decode, ExpiredSignatureError, PyJWTError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from app import db
from models import CollectionItem, User

load_dotenv()


def validate_token(token):
    try:
        with open("pubkey.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )
        logging.info(f"Token: {token}")
        logging.info(f"Public key: {public_key}")
        expected_audience = os.environ["EXPECTED_AUDIENCE"]
        decoded_jwt = decode(
            token, public_key, algorithms=["RS256"], audience=expected_audience
        )
        return decoded_jwt
    except ExpiredSignatureError:
        logging.error("Token is expired")
        return None
    except PyJWTError as e:
        logging.error(f"An error occurred while decoding the token: {e}")
        return None


api_routes = Blueprint("api", __name__)

# USER ROUTES


@api_routes.route("/sign-up", methods=["POST"])
def add_user():
    id = request.json["id"]
    username = request.json["username"]
    email = request.json["email"]
    img = request.json["img"]
    region = request.json["region"]

    user = User(id, username, email, img, region)
    db.session.add(user)
    db.session.commit()

    return f"{user.username}"


@api_routes.route("/<id>/edit", methods=["PUT"])
def update_user(id):
    user = User.query.filter_by(id=id)
    username = request.json["username"]
    email = request.json["email"]
    img = request.json["img"]
    region = request.json["region"]

    user.update(dict(username=username, email=email, img=img, region=region))
    db.session.commit()
    return f"User {username} has been updated"


@api_routes.route("/remove-user/<id>", methods=["DELETE"])
def remove_user(id):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)
    try:
        CollectionItem.query.filter_by(user_id=id).delete()
        User.query.filter_by(id=id).delete()
        db.session.commit()
        return f"User and Collection Items deleted"
    except:
        return "false"


@api_routes.route("/user/<id>", methods=["GET"])
def get_user(id):
    auth_header = request.headers.get("Authorization")
    print(f"Auth Header: {auth_header}")
    token = auth_header.split(" ")[1] if auth_header else None
    print(f"Token: {token}")
    payload = validate_token(token)
    print(f"Payload: {payload}")
    if not payload:
        abort(401)

    try:
        user = User.query.filter_by(id=id).one()
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "img": user.img,
            "region": user.region,
        }
        return jsonify(user_data)
    except:
        return "false"


@api_routes.route("/users", methods=["GET"])
def get_users():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)

    try:
        users = User.query.order_by(User.username.asc()).all()
        user_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "img": user.img,
                "region": user.region,
            }
            user_list.append(user_data)

        return jsonify(user_list)
    except:
        return "false"


# COLLECTION ROUTES


@api_routes.route("/collection-get/<id>", methods=["GET"])
def users_collection(id):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)
    try:
        movies = CollectionItem.query.filter_by(user_id=id).all()
        movie_list = []
        for movie in movies:
            movie_data = {
                "movie_id": movie.movie_id,
                "movie_title": movie.movie_title,
                "movie_year": movie.movie_year,
                "actors": movie.actors,
                "img": movie.img,
                "user_id": movie.user_id,
                "genre": movie.genre,
                "user_score": movie.user_score,
            }
            movie_list.append(movie_data)
        return jsonify(movie_list)
    except:
        return "false"


@api_routes.route("/collection/<username>/<movie_id>", methods=["GET"])
def users_collection_item(id, movie_id):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)

    try:
        movie = CollectionItem.query.filter_by(user_id=id, movie_id=movie_id).one()
        movie_data = {
            "title": movie.movie_title,
            "year": movie.movie_year,
            "actors": movie.actors,
            "img": movie.img,
            "genre": movie.genre,
            "user_score": movie.user_score,
        }
        return jsonify(movie_data)
    except:
        return "false"


@api_routes.route("/collection-add/", methods=["POST"])
def add_to_collection():
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)

    try:
        movie_id = request.json["movie_id"]
        movie_title = request.json["movie_title"]
        movie_year = request.json["movie_year"]
        actors = request.json["actors"]
        img = request.json["img"]
        genre = request.json["genre"]
        user_score = request.json["user_score"]
        user_id = request.json["user_id"]

        item = CollectionItem(
            movie_id, movie_title, movie_year, actors, img, genre, user_score, user_id
        )
        db.session.add(item)
        db.session.commit()
        return f"added item"
    except:
        return "false"


@api_routes.route("/collection-<movie_id>/<user_id>", methods=["PUT"])
def edit_collection_item(user_id, movie_id):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)

    try:
        collectionItem = CollectionItem.query.filter_by(movie_id=movie_id)
        user_id = User.query.filter_by(id=user_id)
        genre = request.json["genre"]
        user_score = request.json["user_score"]

        collectionItem.update(dict(genre=genre, user_score=user_score))
        db.session.commit()
        return f"movie has been updated"
    except:
        return "false"


@api_routes.route("/<user_id>/<movie_id>", methods=["DELETE"])
def remove_collection_item(user_id, movie_id):
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    payload = validate_token(token)
    if not payload:
        abort(401)

    try:
        CollectionItem.query.filter_by(movie_id=movie_id, user_id=user_id).delete()
        db.session.commit()
        return f"this movie has been removed"
    except:
        return "false"
