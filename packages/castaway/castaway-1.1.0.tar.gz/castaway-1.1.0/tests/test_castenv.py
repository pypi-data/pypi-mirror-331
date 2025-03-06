import os
import decimal
import pytest
import castaway


@pytest.fixture
def set_cwd():
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(cwd)


@pytest.fixture
def cfg(set_cwd):
    return castaway.Config(filename=[".env", ".env2"])


def test_default_config(set_cwd):
    config = castaway.config
    config.add_castings(decimal=decimal.Decimal)
    assert config("CASTAWAY_INT", cast=int) == 23
    assert config("CASTAWAY_DECIMAL", cast="decimal") == decimal.Decimal("2.3")


def test_bool(cfg):
    assert cfg("CASTAWAY_TRUE", cast=bool) is True
    assert cfg("CASTAWAY_TRUE_1", cast=bool) is True
    assert cfg("CASTAWAY_TRUE_ON", cast=bool) is True
    assert cfg("CASTAWAY_TRUE_Y", cast=bool) is True
    assert cfg("CASTAWAY_TRUE_YES", cast=bool) is True
    assert cfg("CASTAWAY_NOT_TRUE", cast=bool) is False


def test_emoji(cfg):
    assert cfg("CASTAWAY_NOT_TRUE") == "🤷‍♂️"


def test_list(cfg):
    assert cfg("CASTAWAY_LIST", cast=list) == "a b c".split()


def test_custom_cast(cfg):
    cfg.add_castings(decimal=decimal.Decimal)
    assert cfg("CASTAWAY_DECIMAL", cast="decimal") == decimal.Decimal("3.14159")


def test_override():
    os.environ["CASTAWAY_OVERRIDDEN"] = "I am overriden"
    cfg = castaway.Config()
    assert cfg("CASTAWAY_OVERRIDDEN") == "I am overriden"


def test_not_overridden(cfg):
    assert cfg("CASTAWAY_OVERRIDDEN") != "I should be overridden"


def test_required_failure(cfg):
    with pytest.raises(EnvironmentError):
        cfg("REQUIRED")


def test_dj_database(cfg):
    result = cfg("CASTAWAY_DJ_DATABASE", cast="django_db")
    result.pop("DISABLE_SERVER_SIDE_CURSORS", None)
    assert result == {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {"init_command": "SET storage_engine=InnoDB", "charset": "utf8mb4"},
        "NAME": "dbname",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "host",
        "PORT": 3306,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
    }


def test_dj_email(cfg):
    assert cfg("CASTAWAY_DJ_EMAIL", cast="django_email") == {
        "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
        "EMAIL_FILE_PATH": "",
        "EMAIL_HOST": "localhost",
        "EMAIL_HOST_PASSWORD": "secret",
        "EMAIL_HOST_USER": "site",
        "EMAIL_PORT": 25,
        "EMAIL_USE_TLS": False,
        "EMAIL_USE_SSL": False,
        "EMAIL_TIMEOUT": None,
    }
