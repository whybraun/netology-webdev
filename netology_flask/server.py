from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from schema import CreateAdvertisements, UpdateAdvertisements
from models import Session, Advertisements

app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


def validate_json(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise HttpError(status_code=400, message=error)


def get_advertisements_by_id(advertisements_id: int):
    advertisements = request.session.query(Advertisements).filter_by(id=advertisements_id).first()
    if advertisements is None:
        raise HttpError(status_code=404, message="Advertisement not found")
    return advertisements


def add_advertisements(advertisements):
    try:
        request.session.add(advertisements)
        request.session.commit()
    except IntegrityError:
        request.session.rollback()
        raise HttpError(status_code=409, message="Advertisement already exists")


class AdvertisementsView(MethodView):

    @property
    def session(self) -> Session:
        return request.session

    def get(self, advertisements_id):
        advertisements = get_advertisements_by_id(advertisements_id)
        return jsonify(advertisements.dict)

    def post(self):
        json_data = validate_json(CreateAdvertisements, request.json)
        advertisements = Advertisements(**json_data)
        add_advertisements(advertisements)
        return jsonify({"id": advertisements.id})

    def patch(self, advertisements_id):
        json_data = validate_json(UpdateAdvertisements, request.json)
        advertisements = get_advertisements_by_id(advertisements_id)
        for field, value in json_data.items():
            setattr(advertisements, field, value)
        request.session.commit()
        return jsonify(advertisements)

    def delete(self, advertisements_id):
        advertisements = get_advertisements_by_id(advertisements_id)
        request.session.delete(advertisements)
        request.session.commit()
        return jsonify({'status': 'deleted'})


advertisements_view = AdvertisementsView.as_view("advertisements_view")

app.add_url_rule("/advertisements/", view_func=advertisements_view, methods=["POST"])
app.add_url_rule("/advertisements/<int:advertisements_id>/", view_func=advertisements_view, methods=["GET", "PATCH", "DELETE"])

if __name__ == "__main__":
    app.run()