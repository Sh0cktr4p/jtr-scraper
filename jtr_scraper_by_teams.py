from typing import Dict, List, Tuple
import json
import requests

from bs4 import BeautifulSoup
import numpy as np

JTR_BASE_URL = 'https://turniere.jugger.org'


def get_ranking_page_soup() -> BeautifulSoup:
    global JTR_BASE_URL
    return BeautifulSoup(
        requests.get(JTR_BASE_URL + '/rank.team.php').content,
        'html.parser'
    )


def get_team_names_hrefs() -> List[Tuple[str, str]]:
    return list(map(
        lambda a: (a['title'], a['href']),
        [
            tr.find_all('td')[2].find('a')
            for tr in get_ranking_page_soup().find_all('tr')[1:-1]
        ]
    ))


def get_team_tournaments(team_href: str):
    global JTR_BASE_URL
    team_page_soup = BeautifulSoup(
        requests.get(f"{JTR_BASE_URL}/{team_href}").content,
        'html.parser',
    )

    team_page_table_trs = team_page_soup.find_all('table')[0].find_all('tr')[1:]

    def get_tournament_info_from_tr(tr):
        # print(type(tr))
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

    return list(map(lambda tr: get_tournament_info_from_tr(tr), team_page_table_trs))


def scrape_jtr_by_teams():
    team_names_hrefs = get_team_names_hrefs()

    jtr_by_teams = {}

    for team_name, team_href in team_names_hrefs:
        jtr_by_teams[team_name] = get_team_tournaments(team_href)

    return jtr_by_teams


def calculate_flat_points(placement: int, n_teams: int, points_mapping: Dict[int, int]):
    return (points_mapping[n_teams] / (n_teams - 1)) * (n_teams - placement)

def add_points_information(jtr_by_teams):
    global JTR_BASE_URL
    tournament_sizes = {}  # id -> number of teams

    # Identify all tournament ids and sizes
    for tmts in jtr_by_teams.values():
        for tmt in tmts:
            if tmt['id'] in tournament_sizes:
                # Check for inconsistencies
                assert tournament_sizes[tmt['id']] == tmt['n_teams']
            else:
                tournament_sizes[tmt['id']] = tmt['n_teams']

    points_by_size = {}  # tournament size -> points

    # Get the points for each tournament size
    for id, n_teams in tournament_sizes.items():
        url = f"{JTR_BASE_URL}/tournament.php?id={id}"
        points = int(
            BeautifulSoup(
                requests.get(url).content,
                "html.parser",
            ).find('table').find_all('tr')[-2].find_all('td')[1].text.replace(' Punkte', '')
        )
        if n_teams not in points_by_size:
            points_by_size[n_teams] = []
        points_by_size[n_teams].append(points)

    # Calculate the arg max of points for each tournament size
    points_mapping = {
        n_teams: np.argmax(np.bincount(points_list))
        for n_teams, points_list in points_by_size.items()
    }

    for tmts in jtr_by_teams.values():
        for tmt in tmts:
            tmt['flat_points'] = calculate_flat_points(
                placement=tmt['placement'],
                n_teams=tmt['n_teams'],
                points_mapping=points_mapping,
            )

    return jtr_by_teams


if __name__ == '__main__':
    jtr_by_teams = add_points_information(scrape_jtr_by_teams())

    with open('jtr_by_teams.json', 'w') as f:
        json.dump(jtr_by_teams, f, indent=4, ensure_ascii=False)
