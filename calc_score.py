"""This file contains a script for calculating the score of a team
at a given date.

Author: Felix Trost
"""
from datetime import datetime
import numpy as np
from jtr_scraper import JTR, load_jtr_from_json


def calc_score(team_name: str, date: str, jtr: JTR) -> int:
    """Calculate the score of a team at a given date.

    Args:
        team_name (str): the name of the team
        date (str): the date to calculate the score for
        jtr (JTR): the JTR data

    Returns:
        int: the score of the team at the given date
    """
    ref_time = datetime.strptime(date, "%d.%m.%Y")

    def get_time_factor(ref_time, tmt_date):
        tmt_time = datetime.strptime(tmt_date, "%d.%m.%Y")
        day_diff = (ref_time - tmt_time).days

        if day_diff < 0:
            return 0
        else:
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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("team_name", type=str)
    parser.add_argument(
        "--date",
        "-d",
        type=str,
        default=datetime.now().strftime("%d.%m.%Y"),
    )

    args = parser.parse_args()

    jtr = load_jtr_from_json()

    print(calc_score(args.team_name, args.date, jtr))
