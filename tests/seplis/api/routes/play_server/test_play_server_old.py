import pytest
import sqlalchemy as sa
from seplis import logger
from seplis.api.testbase import client, run_file, AsyncClient, user_signin
from seplis.api import schemas, models
from seplis.api.database import database




if __name__ == '__main__':
    run_file(__file__)