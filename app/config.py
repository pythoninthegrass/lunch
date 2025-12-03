from decouple import config

DEV = config("DEV", default=False, cast=bool)
