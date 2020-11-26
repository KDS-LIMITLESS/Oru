from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import image
from flask_uploads import UploadNotAllowed

from schemas.image import ImageSchema


image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required
    def post(self):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image.save_image(data['image'], save_to_folder=folder)
            basename = image.get_basename(image_path)
            return {"message": f"Image {basename} uploaded!"}, 201
        except UploadNotAllowed:
            wrong_image_path = image.get_basename(data['image'])
            return {"message": f"Error! {wrong_image_path} is not an Image"}, 400

