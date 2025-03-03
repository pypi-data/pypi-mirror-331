import pytest
from jk_soccer_core import Match
from jk_soccer_core.calculations.losses import LossesCalculation


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
        Match(team_a, team_b, 2, 1),
        Match(team_a, team_c, 1, 1),
        Match(team_b, team_a, 0, 3),
        Match(team_c, team_a, 2, 2),
    ]


def test_losses_calculation_team_a(matches, team_a):
    calc = LossesCalculation(team_a)
    assert calc.calculate(matches) == 0


def test_losses_calculation_team_b(matches, team_b):
    calc = LossesCalculation(team_b)
    assert calc.calculate(matches) == 2


def test_losses_calculation_team_c(matches, team_c):
    calc = LossesCalculation(team_c)
    assert calc.calculate(matches) == 0


def test_losses_calculation_empty_team_name(matches):
    calc = LossesCalculation("")
    assert calc.calculate(matches) == 0


def test_losses_calculation_none_team_name(matches):
    calc = LossesCalculation(None)
    assert calc.calculate(matches) == 0


def test_losses_calculation_empty_matches(team_a):
    calc = LossesCalculation(team_a)
    assert calc.calculate([]) == 0


def test_losses_calculation_no_teams():
    match = Match(None, None, 1, 1)
    calc = LossesCalculation("Team A")
    assert calc.calculate([match]) == 0
