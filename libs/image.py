from werkzeug.datastructures import FileStorage
import os
from flask_uploads import IMAGES, UploadSet
from typing import Union

IMAGE_SET = UploadSet('images', IMAGES)


def save_image(image:FileStorage, save_to_folder:str) -> str:
    """ Saves an image to the file storage """
    return IMAGE_SET.save(image, save_to_folder, name=None)

def get_image_path(filename: str =None, folder: str = None) -> str:
    return IMAGE_SET.path(filename, folder)

def get_basename(file:Union[str, FileStorage]) -> str:
    if isinstance(file, FileStorage):
        return file.filename
    return os.path.split(file)[1]



