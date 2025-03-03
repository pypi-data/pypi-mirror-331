import pytest
from jk_soccer_core.models import Match
from jk_soccer_core.calculations.draws import DrawsCalculation


@pytest.fixture
def team_a():
    return "Team A"


@pytest.fixture
def team_b():
    return "Team B"


@pytest.fixture
def team_c():
    return "Team C"


@pytest.fixture
def matches(team_a, team_b, team_c):
    return [
        Match(team_a, team_b, 2, 2),
        Match(team_a, team_c, 1, 1),
        Match(team_b, team_a, 0, 3),
        Match(team_c, team_a, 2, 2),
    ]


def test_draws_calculation_team_a(matches, team_a):
    calc = DrawsCalculation(team_a)
    assert calc.calculate(matches) == 3


def test_draws_calculation_team_b(matches, team_b):
    calc = DrawsCalculation(team_b)
    assert calc.calculate(matches) == 1


def test_draws_calculation_team_c(matches, team_c):
    calc = DrawsCalculation(team_c)
    assert calc.calculate(matches) == 2


def test_draws_calculation_empty_team_name(matches):
    calc = DrawsCalculation("")
    assert calc.calculate(matches) == 0


def test_draws_calculation_none_team_name(matches):
    calc = DrawsCalculation(None)
    assert calc.calculate(matches) == 0


def test_draws_calculation_empty_matches(team_a):
    calc = DrawsCalculation(team_a)
    assert calc.calculate([]) == 0


def test_draws_calculation_no_teams():
    match = Match(None, None, home_score=1, away_score=1)
    calc = DrawsCalculation("Team A")
    assert calc.calculate([match]) == 0
