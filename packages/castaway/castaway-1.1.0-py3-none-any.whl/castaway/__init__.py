import os
from pathlib import Path
import dotenv

required = object()


def cast_bool(val):
    return val.lower() in {"1", "yes", "true", "y", "on"} if isinstance(val, str) else bool(val)


def cast_list(val):
    return [i.strip() for i in val.split(",")]


def cast_django_db(val):
    import dj_database_url

    return dj_database_url.parse(val)


def cast_django_email(val):
    import dj_email_url

    return dj_email_url.parse(val)


class Config:
    def __init__(self, filename=".env", **castings):
        if isinstance(filename, (str, Path)):
            filename = [filename]

        self.filename = [str(f) for f in filename]
        self.found_path = []

        self.castings = {
            bool: cast_bool,
            list: cast_list,
            "django_db": cast_django_db,
            "django_email": cast_django_email,
        }
        self.castings.update(**castings)
        self.values = {}
        for path in self.filename:
            if os.path.exists(path):
                found = path
            else:
                found = dotenv.find_dotenv(path, usecwd=True)

            self.found_path.append(found)
            self.values.update(**dotenv.dotenv_values(found, verbose=True))

    def add_castings(self, **kwargs):
        self.castings.update(kwargs)

    def __call__(self, key, *, default=required, cast=str):
        value = os.getenv(key)
        if value is None:
            value = self.values.get(key, default)

        if value is required:
            raise EnvironmentError(f"{key} is required")

        return None if value is None else self.castings.get(cast, cast)(value)


def __getattr__(name):
    if name == "config":
        return Config()
