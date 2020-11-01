from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from sqlalchemy import and_, func

app = Flask(__name__, static_url_path='')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'grades.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    player = db.Column(db.String(25))
    level = db.Column(db.Integer)
    total_steps = db.Column(db.Integer)
    total_moves = db.Column(db.Integer)
    total_pushes = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __init__(self, player, level, total_steps, total_moves, total_pushes, score):
        self.player = player
        self.level = level
        self.total_steps = total_steps
        self.total_moves = total_moves
        self.total_pushes = total_pushes
        self.score = score

class GameSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'timestamp', 'player', 'level', 'total_steps', 'total_moves', 'total_pushes', 'score')


game_schema = GameSchema()
games_schema = GameSchema(many=True)


# endpoint to create new game
@app.route("/game", methods=["POST"])
def add_game():
    player = request.json['player']
    level = request.json['level']
    total_steps = request.json.get('total_steps', -1)
    total_moves = request.json.get('total_moves', -1)
    total_pushes = request.json.get('total_pushes', -1)
    papertrail = request.json.get('papertrail', "")

    score = 10000 * int(level) - int(total_pushes)*100 - int(total_steps)

    print(player, level, score, papertrail)
    new_game = Game(player, level, total_steps, total_moves, total_pushes, score)

    db.session.add(new_game)
    db.session.commit()

    return game_schema.jsonify(new_game)

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

# endpoint to show highscores 
@app.route("/highscores", methods=["GET"])
def get_game():
    page = request.args.get('page', 1, type=int)

    q = db.session.query(Game.id, Game.timestamp, Game.player, Game.level, func.max(Game.score).label('score'), Game.total_steps).group_by(Game.player).order_by(Game.score.desc(), Game.timestamp.desc())
#    print(q.statement)

    all_games = q.paginate(page, 20, False)
    result = games_schema.dump(all_games.items)
    return jsonify(result)


# endpoint to show player games
@app.route("/highscores/<player>", methods=["GET"])
def game_detail(player):
    game = db.session.query(Game).filter(and_(Game.player == player, Game.score > 0)).order_by(Game.score.desc()).limit(10)
    result = games_schema.dump(game)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
