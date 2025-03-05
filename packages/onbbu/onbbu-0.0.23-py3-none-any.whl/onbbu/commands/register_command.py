from onbbu.settings import COMMANDS


def register_command(cls):
    """Decorator to register commands automatically."""
    COMMANDS[cls.name.lower()] = cls()
    return cls
