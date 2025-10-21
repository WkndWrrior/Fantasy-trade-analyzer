from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from fastapi.responses import FileResponse  # <- moved this to the top

app = FastAPI()

class TradeRequest(BaseModel):
    teamA: List[str]
    teamB: List[str]

def get_player_rankings():
    url = "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php"
    dfs = pd.read_html(url)
    df = dfs[0]
    rankings = {}
    for _, row in df.iterrows():
        name = row["Player"].split(" (")[0]
        rank = row["#"]
        value = 100 - int(rank)
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
        "analysisSummary": f"Team A value: {valueA}, Team B value: {valueB}. {'Team B wins' if diff > 0 else 'Team A wins' if diff < 0 else 'It’s a fair trade'}."
    }

# Serve your OpenAPI YAML file for Custom GPT integration
@app.get("/.well-known/openapi.yaml", include_in_schema=False)
def get_openapi_spec():
    return FileResponse("openapi.yaml", media_type="text/yaml")


