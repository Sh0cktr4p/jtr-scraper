"""This file can be used to scrape the JTR for the results of all past tournaments.

It can be imported as a module to access the data as a list of dictionaries.
"""
from typing import Dict, List
from dataclasses import asdict, dataclass
import requests
from bs4 import BeautifulSoup
import json

JTR_BASE_URL = 'https://turniere.jugger.org'


@dataclass
class Tournament:
    id: int
    date: str
    name: str
    placements: List[str]
    displayed_points: int


def get_tournaments_page_soup() -> BeautifulSoup:
    global JTR_BASE_URL
    tournaments_page = requests.get(f"{JTR_BASE_URL}/index.events.php")
    return BeautifulSoup(tournaments_page.content, "html.parser")


def get_past_tournaments_table_soup() -> BeautifulSoup:
    return get_tournaments_page_soup().find_all("table")[1]  # 0 are upcoming tournaments


def get_tournament_placements(href: str) -> List[str]:
    """Get the placements of all teams in a tournament.
    Sorted, beginning with the winner.
    """
    page = BeautifulSoup(requests.get(f"{JTR_BASE_URL}/{href}").content, "html.parser")
    table = page.find("table")
    trs = table.find_all("tr")[1:]  # Skip header
    return [tr.find_all("td")[2].text for tr in trs]


def get_tournament_displayed_points(href: str) -> List[str]:
    page = BeautifulSoup(requests.get(f"{JTR_BASE_URL}/{href}").content, "html.parser")
    tables = page.find_all("table")
    assert len(tables) == 1
    points_tds = tables[0].find_all("tr")[-2].find_all("td")
    assert len(points_tds) == 2
    assert points_tds[0].text == "Teamwertung: "

    return int(points_tds[1].text.replace(" Punkte", ""))


def get_tournament_from_html_tr(tr: BeautifulSoup) -> Tournament:
    """Get a tournament from a BeautifulSoup tr element."""
    global JTR_BASE_URL

    results_href = tr.find('a', title='Ergebnisse')['href']
    info_href = results_href.replace("tournament.result.php", "tournament.php")
    id = int(results_href.replace("tournament.result.php?id=", ""))
    tds = tr.find_all("td")

    return Tournament(
        id=id,
        date=tds[0].text,
        name=tds[1].text,
        placements=get_tournament_placements(results_href),
        displayed_points=get_tournament_displayed_points(info_href),
    )


def scrape_jtr_to_list() -> List[Tournament]:
    return [
        get_tournament_from_html_tr(tr)
        for tr in get_past_tournaments_table_soup().find_all("tr")[1:]  # Skip header
    ]


def scrape_jtr_to_dict() -> Dict[str, Tournament]:
    return {
        str(tournament.id): tournament
        for tournament in scrape_jtr_to_list()
    }


JTR = scrape_jtr_to_dict()


if __name__ == '__main__':
    with open("jtr.json", "w") as f:
        json.dump(
            {
                id: asdict(tmt) for id, tmt in JTR.items()
            },
            f,
            indent=4,
            ensure_ascii=False
        )
