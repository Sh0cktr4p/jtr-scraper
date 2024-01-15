r"""This file defines a script to collect the JTR history of a list of teams.

Usage:
```
python collect_jtr_history.py \
    [<team_name> ...] (-i <interval>) (-s <start>) (-e <end>)
```

Args:
    team_name (str): the names of the teams to collect the history for
    interval (int): the interval in days between two rows
    start (str): the start date of the history
    end (str): the end date of the history

If the interval between <start> and <end> is not a multiple of <interval>,
the date range will be aligned to the end date.

Author: Felix Trost
"""
from typing import List
from calc_score import calc_score
from jtr_scraper import load_jtr_from_json, JTR
from datetime import datetime

import pandas as pd

from alive_progress import alive_bar


JTR_HISTORY_CSV_PATH = "jtr_history.csv"


def get_first_tmt_date(jtr: JTR) -> datetime:
    """Get the date of the first tournament in the JTR."""
    first_tmt_date = datetime.max

    for tmts in jtr.values():
        for tmt in tmts:
            tmt_date = datetime.strptime(tmt['date'], '%d.%m.%Y')
            if tmt_date < first_tmt_date:
                first_tmt_date = tmt_date

    return first_tmt_date


def get_date_range(
    initial_date: str,
    final_date: str,
    interval: int,
) -> List[str]:
    """Get a list of dates between <initial_date> and <final_date> with
    a given interval.

    If the interval between <initial_date> and <final_date> is not a multiple
    of <interval>, the date range will be aligned to the final date.

    Args:
        initial_date (str): the initial date
        final_date (str): the final date
        interval (int): the interval in days

    Returns:
        List[str]: a list of dates between <initial_date> and <final_date>
    """
    initial_date = datetime.strptime(initial_date, '%d.%m.%Y')
    final_date = datetime.strptime(final_date, '%d.%m.%Y')

    date_range = pd.date_range(
        start=initial_date,
        end=final_date,
        freq=f'{interval}D',
    )

    # Make the date range aligned to the final date
    if len(date_range) > 0:
        date_range += final_date - date_range[-1]

    return [date.strftime('%d.%m.%Y') for date in date_range]


def compute_jtr_history_df(
    teams: List[str],
    initial_date: str,
    final_date: str,
    interval: int,
    jtr: JTR,
) -> pd.DataFrame:
    """Compute the JTR history of a list of teams.

    If the interval between <initial_date> and <final_date> is not a multiple
    of <interval>, the date range will be aligned to the final date.

    Args:
        teams (List[str]): the names of the teams to collect the history for
        initial_date (str): the initial date
        final_date (str): the final date
        interval (int): the interval in days
        jtr (JTR): the JTR data

    Returns:
        pd.DataFrame: a dataframe containing the JTR history of the given teams
    """
    dates = get_date_range(
        initial_date=initial_date,
        final_date=final_date,
        interval=interval,
    )

    history = {}
    with alive_bar(len(teams), title='Collecting JTR history...') as bar:
        for team_name in teams:
            history[team_name] = [
                calc_score(team_name, date, jtr) for date in dates
            ]
            bar()

    df = pd.DataFrame({
        "date": dates,
        **history,
    })

    return df


if __name__ == '__main__':
    import argparse

    jtr = load_jtr_from_json()
    first_tmt_date = get_first_tmt_date(jtr)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "team_names", type=str, nargs="*", default=list(jtr.keys())
    )
    # How many days to skip between two rows
    parser.add_argument(
        "--interval", "-i", type=int, default=7
    )
    parser.add_argument(
        "--start", "-s", type=str, default=first_tmt_date.strftime("%d.%m.%Y")
    )
    parser.add_argument(
        "--end", "-e", type=str, default=datetime.now().strftime("%d.%m.%Y")
    )

    args = parser.parse_args()

    df = compute_jtr_history_df(
        teams=args.team_names,
        initial_date=args.start,
        final_date=args.end,
        interval=args.interval,
        jtr=jtr,
    )

    df.to_csv('jtr_history.csv', index=False)
