import json
from datetime import datetime
import numpy as np


with open("jtr_by_teams.json", "r") as f:
    jtr = json.load(f)


def get_points(team_name: str, date: str) -> int:
    global jtr

    ref_d, ref_m, ref_y = date.split(".")
    ref_time = datetime(int(ref_y), int(ref_m), int(ref_d))

    def get_time_factor(ref_time, tmt_date):
        tmt_d, tmt_m, tmt_y = tmt_date.split(".")
        tmt_time = datetime(int(tmt_y), int(tmt_m), int(tmt_d))
        day_diff = (ref_time - tmt_time).days
        return 0.75 ** int(day_diff / 180)
    
    disc_points = list(map(
        lambda tmt: get_time_factor(
            ref_time=ref_time,
            tmt_date=tmt["date"],
        ) * tmt["flat_points"],
        jtr[team_name],
    ))

    if len(disc_points) < 5:
        disc_points += [0] * (5 - len(disc_points))

    disc_points = np.array(disc_points)
    top_points = disc_points[np.argpartition(disc_points, -5)[-5:]]
    top_points.sort()
    return np.sum(top_points * np.array([0.16, 0.18, 0.20, 0.22, 0.24]))


def _get_points(team_name: str, date: str) -> int:
    global jtr, tmts_by_team, point_mapping

    tmts = [jtr[tmt_id] for tmt_id in tmts_by_team[team_name]]

    points = [point_mapping[str(len(tmt["placements"]))] for tmt in tmts]
    disc_points = [get_discounted_points_for_tmt(
        team_name=team_name,
        reference_date=date,
        tmt=tmt,
        points=points[i],
    ) for i, tmt in enumerate(tmts)]
    if len(disc_points) < 5:
        disc_points += [0] * (5 - len(disc_points))
    disc_points = np.array(disc_points)
    top_points = disc_points[np.argpartition(disc_points, -5)[-5:]]
    top_points.sort()
    return np.sum(top_points * np.array([0.16, 0.18, 0.20, 0.22, 0.24]))


def get_discounted_points_for_tmt(team_name, reference_date, tmt, points):
    placement = tmt["placements"].index(team_name) + 1
    num_teams = len(tmt["placements"])
    tmt_d, tmt_m, tmt_y = tmt["date"].split(".")
    ref_d, ref_m, ref_y = reference_date.split(".")
    day_diff = (
        datetime(int(ref_y), int(ref_m), int(ref_d)) - datetime(int(tmt_y), int(tmt_m), int(tmt_d))
    ).days

    assert day_diff >= 0, f"tmt date: {tmt['date']}, reference date: {reference_date}"
    time_factor = 0.75 ** int(day_diff / 180)
    disc_points = (points / (num_teams - 1)) * (num_teams - placement) * time_factor
    # print(f"{placement}/{num_teams}, TF {time_factor} -> {disc_points}")
    return disc_points


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("team_name", type=str)
    parser.add_argument("--date", type=str, default="09.01.2024")

    args = parser.parse_args()

    print(get_points(args.team_name, args.date))
