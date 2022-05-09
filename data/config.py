from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

USER = env.str('USER_DB')
PASSWORD = env.str('PASSWORD')
HOST = env.str('HOST')
PORT = env.str('PORT')
DATABASE = env.str('DATABASE')


POSTGRES_URI = f"postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "UTC"
}