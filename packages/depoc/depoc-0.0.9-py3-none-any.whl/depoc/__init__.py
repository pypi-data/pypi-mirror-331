import json

from depoc.core.requestor import Requestor
from depoc.core.client import DepocClient
from depoc.core.auth import Connection

from depoc.services.user import User
from depoc.services.owner import Owner
from depoc.services.account import Account
from depoc.services.business import Business
from depoc.services.customer import Customer
from depoc.services.supplier import Supplier


token: str | None = None

try:
    with open('depoc/commands/utils/token.json', 'r') as f:
        data: dict = json.load(f)
        token = data.get('token')
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    pass

# Constants
BASE_URL: str = 'https://api.depoc.com.br'
