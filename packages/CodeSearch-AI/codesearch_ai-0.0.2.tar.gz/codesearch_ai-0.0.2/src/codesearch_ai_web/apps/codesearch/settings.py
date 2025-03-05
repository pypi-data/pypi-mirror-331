"""
This file defines the application settings
"""
import os
from py4web.core import required_folder, Session, Cache, Translator

# Define the app name
APP_NAME = "codesearch"

# Create required folders
app_folder = required_folder(APP_NAME)

# Create translations folder if it doesn't exist
T_FOLDER = os.path.join(app_folder, "translations")
if not os.path.exists(T_FOLDER):
    os.makedirs(T_FOLDER)

# Define session settings (using secure cookies)
SESSION_TYPE = "cookies"
SESSION_SECRET_KEY = "your-secret-key-here"  # Change this in production
session = Session(secret=SESSION_SECRET_KEY)

# Cache settings
CACHE_KEYS = []
cache = Cache(size=1000)

# Translator settings
T = Translator(T_FOLDER) 