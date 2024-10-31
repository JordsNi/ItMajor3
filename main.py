import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Database setup
DATABASE_URL = "polls.db"

# Create tables if they don't exist
def init_db():
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                likes INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER,
                content TEXT,
                FOREIGN KEY (poll_id) REFERENCES polls (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                city TEXT NOT NULL,
                championships INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                jersey_number INTEGER NOT NULL,
                position TEXT NOT NULL,
                team_id INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        ''')
        conn.commit()

init_db()

app = FastAPI()

# Pydantic Models
class PollCreate(BaseModel):
    question: str

class PollUpdate(BaseModel):
    question: str = None

class CommentCreate(BaseModel):
    poll_id: int
    content: str

class CommentUpdate(BaseModel):
    content: str = None

class TeamCreate(BaseModel):
    team_name: str
    city: str
    championships: int

class TeamUpdate(BaseModel):
    team_name: str = None
    city: str = None
    championships: int = None

class PlayerCreate(BaseModel):
    name: str
    jersey_number: int
    position: str
    team_id: int

class PlayerUpdate(BaseModel):
    name: str = None
    jersey_number: int = None
    position: str = None
    team_id: int = None

# Poll Routes
@app.post("/polls/", response_model=PollCreate)
def create_poll(poll: PollCreate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO polls (question) VALUES (?)", (poll.question,))
        conn.commit()
        return poll

@app.get("/polls/")
def get_polls():
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polls")
        polls = cursor.fetchall()
        return [{"id": row[0], "question": row[1], "likes": row[2]} for row in polls]

@app.get("/polls/{poll_id}")
def get_poll(poll_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polls WHERE id = ?", (poll_id,))
        poll = cursor.fetchone()
        if poll is None:
            raise HTTPException(status_code=404, detail="Poll not found")
        return {"id": poll[0], "question": poll[1], "likes": poll[2]}

@app.put("/polls/{poll_id}", response_model=PollUpdate)
def update_poll(poll_id: int, poll_update: PollUpdate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        existing_poll = cursor.execute("SELECT * FROM polls WHERE id = ?", (poll_id,)).fetchone()
        if existing_poll is None:
            raise HTTPException(status_code=404, detail="Poll not found")
        
        updated_question = poll_update.question if poll_update.question is not None else existing_poll[1]

        cursor.execute("UPDATE polls SET question = ? WHERE id = ?", (updated_question, poll_id))
        conn.commit()
        return {"id": poll_id, "question": updated_question, "likes": existing_poll[2]}

@app.delete("/polls/{poll_id}")
def delete_poll(poll_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM polls WHERE id = ?", (poll_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Poll not found")
        return {"detail": "Poll deleted successfully"}

# Comment Routes
@app.post("/comments/", response_model=CommentCreate)
def create_comment(comment: CommentCreate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (poll_id, content) VALUES (?, ?)", (comment.poll_id, comment.content))
        conn.commit()
        return comment

@app.get("/comments/")
def get_comments():
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments")
        comments = cursor.fetchall()
        return [{"id": row[0], "poll_id": row[1], "content": row[2]} for row in comments]

@app.get("/comments/{comment_id}")
def get_comment(comment_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id,))
        comment = cursor.fetchone()
        if comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"id": comment[0], "poll_id": comment[1], "content": comment[2]}

@app.put("/comments/{comment_id}", response_model=CommentUpdate)
def update_comment(comment_id: int, comment_update: CommentUpdate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        existing_comment = cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
        if existing_comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        updated_content = comment_update.content if comment_update.content is not None else existing_comment[2]

        cursor.execute("UPDATE comments SET content = ? WHERE id = ?", (updated_content, comment_id))
        conn.commit()
        return {"id": comment_id, "poll_id": existing_comment[1], "content": updated_content}

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"detail": "Comment deleted successfully"}

# Team Routes
@app.post("/teams/", response_model=TeamCreate)
def create_team(team: TeamCreate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teams (team_name, city, championships) VALUES (?, ?, ?)", 
                       (team.team_name, team.city, team.championships))
        conn.commit()
        return team

@app.get("/teams/")
def get_teams():
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams")
        teams = cursor.fetchall()
        return [{"id": row[0], "team_name": row[1], "city": row[2], "championships": row[3]} for row in teams]

@app.get("/teams/{team_id}")
def get_team(team_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"id": team[0], "team_name": team[1], "city": team[2], "championships": team[3]}

@app.put("/teams/{team_id}", response_model=TeamUpdate)
def update_team(team_id: int, team_update: TeamUpdate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        existing_team = cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
        if existing_team is None:
            raise HTTPException(status_code=404, detail="Team not found")
        
        updated_team_name = team_update.team_name if team_update.team_name is not None else existing_team[1]
        updated_city = team_update.city if team_update.city is not None else existing_team[2]
        updated_championships = team_update.championships if team_update.championships is not None else existing_team[3]

        cursor.execute("UPDATE teams SET team_name = ?, city = ?, championships = ? WHERE id = ?",
                       (updated_team_name, updated_city, updated_championships, team_id))
        conn.commit()
        return {"id": team_id, "team_name": updated_team_name, "city": updated_city, "championships": updated_championships}

@app.delete("/teams/{team_id}")
def delete_team(team_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"detail": "Team deleted successfully"}

# Player Routes
@app.post("/players/", response_model=PlayerCreate)
def create_player(player: PlayerCreate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name, jersey_number, position, team_id) VALUES (?, ?, ?, ?)", 
                       (player.name, player.jersey_number, player.position, player.team_id))
        conn.commit()
        return player

@app.get("/players/")
def get_players():
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players")
        players = cursor.fetchall()
        return [{"id": row[0], "name": row[1], "jersey_number": row[2], "position": row[3], "team_id": row[4]} for row in players]

@app.get("/players/{player_id}")
def get_player(player_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        player = cursor.fetchone()
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return {"id": player[0], "name": player[1], "jersey_number": player[2], "position": player[3], "team_id": player[4]}

@app.put("/players/{player_id}", response_model=PlayerUpdate)
def update_player(player_id: int, player_update: PlayerUpdate):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        existing_player = cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
        if existing_player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        
        updated_name = player_update.name if player_update.name is not None else existing_player[1]
        updated_jersey_number = player_update.jersey_number if player_update.jersey_number is not None else existing_player[2]
        updated_position = player_update.position if player_update.position is not None else existing_player[3]
        updated_team_id = player_update.team_id if player_update.team_id is not None else existing_player[4]

        cursor.execute("UPDATE players SET name = ?, jersey_number = ?, position = ?, team_id = ? WHERE id = ?",
                       (updated_name, updated_jersey_number, updated_position, updated_team_id, player_id))
        conn.commit()
        return {"id": player_id, "name": updated_name, "jersey_number": updated_jersey_number, "position": updated_position, "team_id": updated_team_id}

@app.delete("/players/{player_id}")
def delete_player(player_id: int):
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Player not found")
        return {"detail": "Player deleted successfully"}
