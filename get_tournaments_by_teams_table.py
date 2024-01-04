import json

with open("jtr.json", "r") as f:
    jtr = json.load(f)

table = {}

for id, tmt in jtr.items():
    for placement in tmt["placements"]:
        if placement["team"] not in table:
            table[placement["team"]] = []
        table[placement["team"]].append({"id": id, "spot": placement["spot"]})


with open("tmts_by_team.json", "w") as f:
    json.dump(table, f, indent=4, sort_keys=True, ensure_ascii=False)
