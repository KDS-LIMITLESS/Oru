from quart_openapi import PintBlueprint

user = PintBlueprint("user", __name__)

from . import resources