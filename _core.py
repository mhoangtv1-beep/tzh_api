class Enum(object):
    @classmethod
    def get(cls, value, default=None):
        for k, v in cls.__dict__.items():
            if v == value:
                return v
        return default
