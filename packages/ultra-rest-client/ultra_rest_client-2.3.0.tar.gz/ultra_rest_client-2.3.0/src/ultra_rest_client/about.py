__version__ = "2.3.0"
PREFIX = "udns-python-rest-client-"

def get_client_user_agent():
    return f"{PREFIX}{__version__}"