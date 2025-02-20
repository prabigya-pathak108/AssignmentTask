from decouple import config


class SingletonClass(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


class SecretManager(SingletonClass):
    def get_from_env(self, key: str, cast=str, default=None):
        return (
            config(key) if default is None else config(key, cast=cast, default=default)
        )
    
