from . import make_fire_cmd
import fire

def echo(*args, **kwargs):
    return {'args': args, 'kwargs': kwargs}

fire.Fire(make_fire_cmd(echo))
