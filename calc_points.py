import json
from datetime import datetime
import numpy as np


with open("jtr.json", "r") as f:
    jtr = json.load(f)


with open("tmts_by_team.json", "r") as f:
    tmts_by_team = json.load(f)


with open("point_mapping.json", "r") as f:
    point_mapping = json.load(f)


def get_points(team_name: str, date: str) -> int:
    global jtr, tmts_by_team, point_mapping

    tmts = [(jtr[tmt["id"]], tmt["spot"]) for tmt in tmts_by_team[team_name]]

    points = [point_mapping[str(len(tmt["placements"]))] for tmt, _ in tmts]
    disc_points = [get_discounted_points_for_tmt(
        team_name=team_name,
        spot=spot,
        reference_date=date,
        tmt=tmt,
        points=points[i],
    ) for i, (tmt, spot) in enumerate(tmts)]
    if len(disc_points) < 5:
        disc_points += [0] * (5 - len(disc_points))
    disc_points = np.array(disc_points)
    top_points = disc_points[np.argpartition(disc_points, -5)[-5:]]
    top_points.sort()
    # print(top_points * np.array([0.16, 0.18, 0.20, 0.22, 0.24]))
    return np.sum(top_points * np.array([0.16, 0.18, 0.20, 0.22, 0.24]))


def get_discounted_points_for_tmt(team_name, spot, reference_date, tmt, points):
    tmt_d, tmt_m, tmt_y = tmt["date"].split(".")
    ref_d, ref_m, ref_y = reference_date.split(".")
    day_diff = (
        datetime(int(ref_y), int(ref_m), int(ref_d)) - datetime(int(tmt_y), int(tmt_m), int(tmt_d))
    ).days

    if day_diff < 0:
        return 0

    num_teams = len(tmt["placements"])
    time_factor = 0.75 ** int(day_diff / 180)
    disc_points = (points / (num_teams - 1)) * (num_teams - spot) * time_factor
    # print(f"{spot}/{num_teams}, TF {time_factor} -> {disc_points}")
    return disc_points


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("team_name", type=str)
    parser.add_argument("--date", type=str, default="01.01.2024")

    args = parser.parse_args()

    print(get_points(args.team_name, args.date))
