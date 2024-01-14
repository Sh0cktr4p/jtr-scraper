"""This file contains a script for comparing the scores of this
implementation to the scores displayed in the JTR.

Author: Felix Trost
"""
from calc_score import calc_score
import matplotlib.pyplot as plt
import numpy as np
from jtr_scraper import get_ranking_page_soup


if __name__ == "__main__":
    date = "04.01.2024"

    jtr_ranking_table = get_ranking_page_soup().find(
        "table"
    ).find_all(
        "tr"
    )[1:-1]  # Skip header

    teams = [tr.find_all("td")[2].text for tr in jtr_ranking_table]

    official_scores = [
        float(tr.find_all("td")[5].text) for tr in jtr_ranking_table
    ]
    my_scores = [calc_score(team, date) for team in teams]

    plt.plot(np.arange(len(teams)), official_scores, label="JTR")
    plt.plot(np.arange(len(teams)), my_scores, label="Mine")
    plt.legend()
    plt.show()
