import json

with open("jtr.json", "r") as f:
    jtr = json.load(f)

table = {}

for id, tmt in jtr.items():
    for team in tmt["placements"]:
        if team not in table:
            table[team] = []
        table[team].append(id)

sorted_table = {
    team: sorted(tmts)
    for team, tmts in table.items()
}

with open("tmts_by_team.json", "w") as f:
    json.dump(sorted_table, f, indent=4, sort_keys=True, ensure_ascii=False)
