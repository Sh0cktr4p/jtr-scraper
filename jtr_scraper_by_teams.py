from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
import json

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

    team_page_table_trs = [
        team_page_soup.find_all('table')[0].find_all('tr')[1:]
    ]

    def get_tournament_info_from_tr(tr):
        print(type(tr))
        tds = tr.find_all('td')
        tournament_a = tds[1].find('a')

        id = tournament_a['href'].replace('tournament.php?id=', '')
        date = tds[0].text
        name = tournament_a['title']
        placement, n_teams = tds[2].text.split('/')

        return {
            'id': id,
            'date': date,
            'name': name,
            'placement': placement,
            'n_teams': n_teams,
        }

    return list(map(lambda tr: get_tournament_info_from_tr(tr), team_page_table_trs))


def scrape_jtr_by_teams():
    team_names_hrefs = get_team_names_hrefs()

    jtr_by_teams = {}

    for team_name, team_href in team_names_hrefs:
        jtr_by_teams[team_name] = get_team_tournaments(team_href)

    return jtr_by_teams


if __name__ == '__main__':
    jtr_by_teams = scrape_jtr_by_teams()

    with open('jtr_by_teams.json', 'w') as f:
        json.dump(jtr_by_teams, f, indent=4, ensure_ascii=False)
