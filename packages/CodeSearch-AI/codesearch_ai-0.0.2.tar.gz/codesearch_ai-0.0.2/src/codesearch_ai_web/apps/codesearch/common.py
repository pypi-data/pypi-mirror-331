"""
This file defines cache, session, and translator objects for the app
"""
import os
import logging
from py4web import Session, Cache, Translator, DAL, Field
from py4web.utils.auth import Auth
from py4web.utils.downloader import downloader
from pydal.validators import *
from py4web.utils.factories import ActionFactory
from . import settings
import datetime

# Define database and tables
db = DAL(
    "sqlite://storage.db",
    folder=os.path.join(os.path.dirname(__file__), "databases"),
    pool_size=1,
    migrate=True,
    fake_migrate=False,
)

# Define conversation tables
db.define_table('conversations',
    Field('title', 'string', required=True),
    Field('directory_path', 'string', required=True),
    Field('created_at', 'datetime', default=lambda: datetime.datetime.now()),
    Field('updated_at', 'datetime', default=lambda: datetime.datetime.now(), update=lambda: datetime.datetime.now()),
)

db.define_table('messages',
    Field('conversation_id', 'reference conversations', required=True),
    Field('role', 'string', required=True),
    Field('content', 'text', required=True),
    Field('created_at', 'datetime', default=lambda: datetime.datetime.now()),
)

# Define global objects that may be needed by all actions
cache = settings.cache
T = settings.T

# Use session from settings
session = settings.session

# Define convenience action factory
action = ActionFactory(session)

# Add CORS headers to all actions
def _enable_cors(action):
    def wrapper(*args, **kwargs):
        from py4web import HTTP
        response = action(*args, **kwargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return wrapper

# Wrap the action factory to include CORS
action.uses = lambda *a: lambda f: _enable_cors(action.uses(*a)(f))

# Logger
logger = logging.getLogger("py4web:app:codesearch")
logger.setLevel(logging.INFO)

# Define your auth object
auth = Auth(session, db, define_tables=False)
auth.enable = False 