from database.DatabaseWrapper import DatabaseWrapper
from models.game import Game
from models.player import Player
from models.score import Score
import datetime
from dataclasses import asdict


from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world!'