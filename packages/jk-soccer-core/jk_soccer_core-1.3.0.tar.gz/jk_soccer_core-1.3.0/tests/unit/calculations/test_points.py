import pytest
from jk_soccer_core.models import Match
from jk_soccer_core.calculations.points import PointsCalculation


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
        Match(team_a, team_b, 2, 2),  # Draw
        Match(team_a, team_c, 1, 0),  # Team A wins
        Match(team_b, team_a, 0, 3),  # Team A wins
        Match(team_c, team_a, 2, 1),  # Team A loses
    ]


def test_points_calculation_team_a(matches, team_a):
    calc = PointsCalculation(team_a)
    assert calc.calculate(matches) == 7  # 2 wins (6 points) + 1 draw (1 point)


def test_points_calculation_team_b(matches, team_b):
    calc = PointsCalculation(team_b)
    assert calc.calculate(matches) == 1  # 1 draw (1 point)


def test_points_calculation_team_c(matches, team_c):
    calc = PointsCalculation(team_c)
    assert calc.calculate(matches) == 3  # 1 win (3 points)


def test_points_calculation_empty_team_name(matches):
    calc = PointsCalculation("")
    assert calc.calculate(matches) == 0


def test_points_calculation_none_team_name(matches):
    calc = PointsCalculation(None)
    assert calc.calculate(matches) == 0


def test_points_calculation_empty_matches(team_a):
    calc = PointsCalculation(team_a)
    assert calc.calculate([]) == 0


def test_points_calculation_no_teams():
    match = Match(None, None, 1, 1)
    calc = PointsCalculation("Team A")
    assert calc.calculate([match]) == 0
