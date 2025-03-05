class BaseCommand:
    """Base class for all commands."""

    name: str
    help: str = "Base command description"

    def __init__(self):
        self.parser = None

    def add_arguments(self, parser):
        """Override this method to add custom arguments."""
        pass

    def handle(self, *args, **kwargs):
        """Override this method to implement command logic."""
        raise NotImplementedError("Subclasses must implement handle()")