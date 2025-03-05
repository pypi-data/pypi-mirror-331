"""
This is the codesearch application, a web interface for dir-assistant
"""
from py4web import action, request, abort, redirect, URL, Field
from py4web.core import required_folder
from py4web.utils.form import Form
from py4web.utils.factories import ActionFactory
from .common import db, session, T, cache, auth, logger

# Create required folders
required_folder('codesearch')

# Import controllers after creating required folders
from .controllers import *

# Define your tables below
db.commit()

# Make this the default app
app = ActionFactory(session)

# Define your http actions below 