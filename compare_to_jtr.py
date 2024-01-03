from calc_points import get_points
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np

JTR_BASE_URL = 'https://turniere.jugger.org'

JTR_RANKING_TABLE = BeautifulSoup(
    requests.get(f"{JTR_BASE_URL}/rank.team.php").content
).find("table").find_all("tr")[1:-1]  # Skip header

teams = [tr.find_all("td")[2].text for tr in JTR_RANKING_TABLE]
jtr_points = [float(tr.find_all("td")[5].text) for tr in JTR_RANKING_TABLE]
my_points = [get_points(team, "24.12.2023") for team in teams]

plt.plot(np.arange(len(teams)), jtr_points, label="JTR")
plt.plot(np.arange(len(teams)), my_points, label="Mine")
plt.legend()
plt.show()
