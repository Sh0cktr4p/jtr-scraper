import json
import matplotlib.pyplot as plt
import numpy as np


with open("jtr.json", "r") as f:
    jtr = json.load(f)


points = {}

for tmt in jtr.values():
    num_teams = len(tmt["placements"])
    if num_teams not in points:
        points[num_teams] = []
    points[num_teams].append(tmt["displayed_points"])

point_mapping = {
    num_teams: np.median(points_list)
    for num_teams, points_list in points.items()
}

with open("point_mapping.json", "w") as f:
    json.dump(point_mapping, f, indent=4, sort_keys=True)

plt.scatter(point_mapping.keys(), point_mapping.values())
plt.show()
