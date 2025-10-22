from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
from fastapi.responses import FileResponse

app = FastAPI()

class TradeRequest(BaseModel):
    teamA: List[str]
    teamB: List[str]

def get_player_rankings():
    url = "https://api.sleeper.app/v1/players/nfl"
    response = requests.get(url)
    all_players = response.json()

    rankings = {}
    for player_id, player in all_players.items():
        if player.get("position") in ["QB", "RB", "WR", "TE"]:
            name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            # Assign values based on position
            base_values = {
                "QB": 90,
                "RB": 85,
                "WR": 80,
                "TE": 75
            }
            value = base_values.get(player["position"], 50)
            rankings[name] = value

    return rankings

def calculate_grade(difference):
    if difference >= 20:
        return "A"
    elif difference >= 10:
        return "B"
    elif difference >= 0:
        return "C+"
    elif difference >= -10:
        return "C"
    elif difference >= -20:
        return "D"
    else:
        return "F"

@app.post("/api/analyze")
def analyze_trade(trade: TradeRequest):
    player_values = get_player_rankings()

    valueA = sum(player_values.get(p, 50) for p in trade.teamA)
    valueB = sum(player_values.get(p, 50) for p in trade.teamB)

    diff = valueB - valueA
    teamAGrade = calculate_grade(-diff)
    teamBGrade = calculate_grade(diff)

    return {
        "teamAGrade": teamAGrade,
        "teamBGrade": teamBGrade,
        "analysisSummary": f"Team A value: {valueA}, Team B value: {valueB}. "
                           f"{'Team B wins' if diff > 0 else 'Team A wins' if diff < 0 else 'It’s a fair trade'}."
    }

# Serve OpenAPI file for GPT actions
@app.get("/.well-known/openapi.yaml", include_in_schema=False)
def get_openapi_spec():
    return FileResponse("openapi.yaml", media_type="text/yaml")



