import pandas as pd
import numpy as np
from calc_points import get_points
from datetime import datetime, timedelta
import json


if __name__ == "__main__":
    with open("tmts_by_team.json", "r") as f:
        tmts_by_team = json.load(f)

    x = []
    date = datetime(2009, 1, 1)
    while (date < datetime(2024, 2, 1)):
        x.append(f"{date.day}.{date.month}.{date.year}")
        print(date)
        date += timedelta(days=7)
    df = pd.DataFrame(dict(date=x))

    for team in tmts_by_team:
        print(team)
        df[team] = [get_points(team, d) for d in x]

    df.to_csv("jtr_history.csv", index=False)
