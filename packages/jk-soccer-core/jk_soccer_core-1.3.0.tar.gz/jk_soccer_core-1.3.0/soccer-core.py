import marimo

__generated_with = "0.11.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Jedi-Knights

        ## Soccer Core Notebook
        """
    )
    return (mo,)


@app.cell
def _():
    import csv

    from typing import Iterable
    from datetime import datetime
    from jk_soccer_core.models.match import Match

    def read_matches(file_path: str) -> Iterable[Match]:
        matches = []

        with open(file_path, mode="r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                match = Match(
                    home_team=row["home_team"],
                    away_team=row["away_team"],
                    home_score=int(row["home_score"]),
                    away_score=int(row["away_score"]),
                    date=datetime.strptime(row["start_date"], "%Y-%m-%d").date(),
                    time=datetime.strptime(row["start_time"], "%H:%M:%S").time(),
                )

                matches.append(match)

        return matches

    def display_matches(matches: Iterable[Match]):
        for match in matches:
            print(match)

    matches = read_matches("./data/match_data_1.csv")
    display_matches(matches)
    return (
        Iterable,
        Match,
        csv,
        datetime,
        display_matches,
        matches,
        read_matches,
    )


@app.cell
def _(matches, mo):
    # from marimo import Dropdown

    from jk_soccer_core.models.match import get_team_names

    teams = mo.ui.dropdown(sorted(get_team_names(matches)))
    teams

    mo.md(
        f"""
        The `marimo.ui` module has a library of pre-built elements.

        For example, here's the teams 
        
        `Teams`: {teams}
        """
    )

    # mo.md(f"There are {len(matches)} teams.")

    return get_team_names, teams


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
