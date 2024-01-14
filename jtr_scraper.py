"""This file contains a script for scraping the JTR website
and storing the data in a JSON file.

Author: Felix Trost
"""
from typing import Any, Dict, List, Tuple
import json
import requests

from bs4 import BeautifulSoup
import numpy as np


JTR_BASE_URL = 'https://turniere.jugger.org'
JTR_JSON_PATH = 'jtr.json'

TournamentInfo = Dict[str, Any]
JTR = Dict[str, List[TournamentInfo]]


def get_ranking_page_soup() -> BeautifulSoup:
    """Get a BeautifulSoup object for the team ranking page of the JTR."""
    global JTR_BASE_URL
    return BeautifulSoup(
        requests.get(f"{JTR_BASE_URL}/rank.team.php").content,
        'html.parser'
    )


def get_team_names_hrefs() -> List[Tuple[str, str]]:
    """Get a list of (team name, page href) tuples for each team on the JTR."""
    return list(map(
        lambda a: (a['title'], a['href']),
        [
            tr.find_all('td')[2].find('a')
            for tr in get_ranking_page_soup().find_all('tr')[1:-1]
        ]
    ))


def get_team_tournaments(team_href: str) -> List[TournamentInfo]:
    """Get a list of tournament information for a given team.

    The tournament information contains:
    - id: the id of the tournament
    - date: the date of the tournament
    - name: the name of the tournament
    - placement: the placement of the given team in the tournament
    - n_teams: the total number of teams in the tournament

    Args:
        team_href (str): the href of the team on the JTR website

    Returns:
        List[TournamentInfo]: a list of tournament information
    """
    global JTR_BASE_URL
    team_page_soup = BeautifulSoup(
        requests.get(f"{JTR_BASE_URL}/{team_href}").content,
        'html.parser',
    )

    team_page_table_trs = team_page_soup.find_all(
        'table'
    )[0].find_all(
        'tr'
    )[1:]

    def get_tournament_info_from_tr(tr):
        tds = tr.find_all('td')
        tournament_a = tds[1].find('a')

        id = tournament_a['href'].replace('tournament.php?id=', '')
        date = tds[0].text
        name = tournament_a['title']

        placement, n_teams = tds[3].text.split('/')

        return {
            'id': id,
            'date': date,
            'name': name,
            'placement': int(placement),
            'n_teams': int(n_teams),
        }

    return list(map(
        lambda tr: get_tournament_info_from_tr(tr),
        team_page_table_trs
    ))


def calculate_flat_points(
    placement: int,
    n_teams: int,
    point_weight_mapping: Dict[int, int],
) -> int:
    """Calculate the points of a tournament without temporal decay.

    Args:
        placement (int): the placement of the given team in the tournament
        n_teams (int): the total number of teams in the tournament
        point_weight_mapping (Dict[int, int]): the nonlinear mapping
            from tournament sizes to point weights"""
    return (
        point_weight_mapping[n_teams] / (n_teams - 1)
    ) * (n_teams - placement)


def get_tournament_sizes(
    jtr: JTR,
) -> Dict[str, int]:
    """Get a mapping from tournament ids to tournament sizes.

    Args:
        jtr (JTR): a dictionary of team names
            to a list of tournament information for all attended tournaments
            of that team

    Returns:
        Dict[str, int]: a mapping from tournament ids to tournament sizes
    """
    tournament_sizes = {}  # id -> number of teams

    # Identify all tournament ids and sizes
    for tmts in jtr.values():
        for tmt in tmts:
            if tmt['id'] in tournament_sizes:
                # Check for inconsistencies
                assert tournament_sizes[tmt['id']] == tmt['n_teams']
            else:
                tournament_sizes[tmt['id']] = tmt['n_teams']

    return tournament_sizes


def get_tournament_displayed_point_weight(id: str) -> int:
    """Get the point weight displayed on the JTR website
    for a given tournament.
    These may be incorrect due to inconsistencies of the JTR website!

    Args:
        id (str): the id of the tournament

    Returns:
        int: the point weight displayed on the JTR website
            for a given tournament
    """
    global JTR_BASE_URL
    url = f"{JTR_BASE_URL}/tournament.php?id={id}"
    return int(
        BeautifulSoup(
            requests.get(url).content,
            "html.parser",
        ).find('table').find_all('tr')[-2].find_all('td')[1].text.replace(
            ' Punkte',
            ''
        )
    )


def get_tmt_size_to_point_weight_mapping(
    jtr: JTR,
) -> Dict[int, int]:
    """Get a mapping from tournament sizes to point weights.

    Scrape all tournaments for their displayed point weights and
    take the most frequent one for each tournament size.

    This is necessary because the JTR website contains inconsistencies
    in the displayed point weights.

    Args:
        jtr (JTR): a dictionary of team names
            to a list of tournament information for all attended tournaments
            of that team

    Returns:
        Dict[int, int]: a mapping from tournament sizes to point weights
    """
    tournament_sizes = get_tournament_sizes(jtr)  # id -> number of teams

    points_by_size = {}  # tournament size -> points

    for id, n_teams in tournament_sizes.items():
        points_by_size.setdefault(n_teams, []).append(
            get_tournament_displayed_point_weight(id)
        )

    return {
        n_teams: np.argmax(np.bincount(points_list))
        for n_teams, points_list in points_by_size.items()
    }


def _add_flat_points_information(
    jtr: JTR,
) -> None:
    """Add the flat points to the tournament information in-place.

    Args:
        jtr (JTR): a dictionary of team names
            to a list of tournament information for all attended tournaments
            of that team. The flat points are added in-place.
    """
    point_weight_mapping = get_tmt_size_to_point_weight_mapping(jtr)

    for tmts in jtr.values():
        for tmt in tmts:
            tmt['flat_points'] = calculate_flat_points(
                placement=tmt['placement'],
                n_teams=tmt['n_teams'],
                point_weight_mapping=point_weight_mapping,
            )


def scrape_jtr() -> JTR:
    """Scrape the JTR website and return a dictionary
    of team names to tournament information.

    The tournament information contains:
    - id: the id of the tournament
    - date: the date of the tournament
    - name: the name of the tournament
    - placement: the placement of the given team in the tournament
    - n_teams: the total number of teams in the tournament
    - flat_points: the points of the tournament without temporal decay

    Returns:
        JTR: a dictionary
            of team names to tournament information
    """
    jtr = {
        team_name: get_team_tournaments(team_href)
        for team_name, team_href in get_team_names_hrefs()
    }

    _add_flat_points_information(jtr)

    return jtr


if __name__ == '__main__':
    jtr = scrape_jtr()

    with open(JTR_JSON_PATH, 'w') as f:
        json.dump(jtr, f, indent=4, ensure_ascii=False)
