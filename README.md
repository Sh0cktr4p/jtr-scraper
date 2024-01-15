# JTR Scraper

Can be used to scrape the [JTR website](turniere.jugger.org/) to a .json file containing information about every tournament every team on the JTR has participated in.

The jtr.json file contains the names of the teams as keys and lists of tournament data as values.
The tournament data contains:

- id: the tournament's id in the jtr
- name: the name of the tournament
- date: the date of the tournament in the format "%d.%m.%Y"
- n_teams: the number of teams participating in the tournament
- placement: the placement of the given team in the tournament
- flat_points: the undiscounted points given for the tournament

# Installation

To install the prerequisites, execute:

```
pip install -r requirements.txt
```

# Execution

To generate the `jtr.json` file, execute:

```
python scrape_jtr.py
```

To compute the score of any team at any point in time, run:

```
python calc_score.py <team_name> (-d <date>)
```

where:
- `<date>` is a string containing the date for which the score is requested.
It should be given in the format `%d.%m.%Y`, e.g., `"01.01.2024"`. Default value: the date of execution


To generate a `jtr_history.csv` file containing all scores of a list of teams in a given time interval, run:

```
python collect_jtr_history.py [<team_name> ...] (-i <interval>) (-s <start>) (-e <end>)
```

where:
- `[<team_name> ...]` is a list of team names. Leave out to include all teams
- `<interval>` is the number of days between the measurements. Default value: 7 days
- `<start>` is the start date of the time period. Default value: date of first tournament in the JTR (22.02.2009)
- `<end>` is the end date of the time period. Default value: the date of execution

`<start>` and `<end>` are strings containing the date for which the score is requested.
They should be given in the format `%d.%m.%Y`, e.g., `"01.01.2024"`.

If the number of days between `<start>` and `<end>` is not divisible by `<interval>`, the measurement dates are aligned with `<end>` (the last measurement is guaranteed to be at `<end>`).