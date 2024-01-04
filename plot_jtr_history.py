import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
from matplotlib import dates

if __name__ == "__main__":
    df = pd.read_csv("jtr_history.csv")
    time = [datetime.strptime(d, '%d.%m.%Y').date() for d in df["date"]]

    colors = {
        "Munich Monks": "orange",
        "Rigor Mortis": "red",
        "Zonenkinder": "olive",
        "Jugger Basilisken Basel": "green",
        "LARP & Quidditch Verein München": "black",
        "Peters Pawns": "yellow",
        "HaWu AllstarZ": "purple",
        "Jugger Helden Bamberg": "brown",
    }

    ps = df.columns[1:]

    plt.gca().xaxis.set_major_formatter(dates.DateFormatter('%d.%m.%Y'))
    plt.gca().xaxis.set_major_locator(dates.YearLocator())

    for p in colors:
        plt.plot(time, df[p], label=p, color=colors[p])

    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.show()
