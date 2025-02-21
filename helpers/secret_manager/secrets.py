from decouple import config


class SingletonClass(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


class SecretManager(SingletonClass):
    def get_from_env(self, key: str, default=None, cast=str):
        value = config(key, default=default, cast=cast)
        return value if value is not None else default
    
