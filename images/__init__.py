from quart_openapi import PintBlueprint

images = PintBlueprint("image", __name__)

from . import resource
