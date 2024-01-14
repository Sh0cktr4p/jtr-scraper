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
pip install requests
pip install beautifulsoup4
pip install json
pip install numpy
pip install matplotlib
pip install alive-progress
```

# Execution

To generate the `jtr.json` file, execute

```
python scrape_jtr.py
```
