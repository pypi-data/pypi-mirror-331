import pytest
from jk_soccer_core.models import Match
from jk_soccer_core.calculations.percentages import (
    WinningPercentageCalculation,
    OpponentsWinningPercentageCalculation,
)


@pytest.fixture
def teams():
    return (
        "Team A",
        "Team B",
        "Team C",
        "Team D",
        "Team E",
        "Team F",
        "Team G",
        "Team H",
        "Team I",
    )


@pytest.fixture
def matches(teams):
    team_a, team_b, team_c, team_d, team_e, team_f, team_g, team_h, team_i = teams
    return [
        Match(team_a, team_b, 1, 0),
        Match(team_a, team_c, 2, 1),
        Match(team_a, team_d, 1, 1),
        Match(team_b, team_c, 2, 1),
        Match(team_a, team_b, 0, 1),
        # Team E wins all matches
        Match(team_e, team_f, 3, 0),
        Match(team_e, team_g, 2, 1),
        # Team F loses all matches
        Match(team_f, team_h, 0, 2),
        Match(team_f, team_i, 1, 3),
    ]


def test_winning_percentage_calculation_no_team_name(matches):
    calc = WinningPercentageCalculation(None, None)
    assert calc.calculate(matches) == 0.0


def test_winning_percentage_calculation_empty_team_name(matches):
    calc = WinningPercentageCalculation("", None)
    assert calc.calculate(matches) == 0.0


def test_winning_percentage_calculation_all_wins(matches):
    calc = WinningPercentageCalculation("Team E", None)
    assert calc.calculate(matches) == 1.0  # 2 wins, 0 draws, 0 losses


def test_winning_percentage_calculation_all_losses(matches):
    calc = WinningPercentageCalculation("Team F", None)
    assert calc.calculate(matches) == 0.0  # 0 wins, 0 draws, 2 losses


def test_winning_percentage_calculation_all_draws(teams):
    matches = [
        Match("Team A", "Team B", 1, 1),
        Match("Team A", "Team C", 2, 2),
        Match("Team A", "Team D", 0, 0),
    ]
    calc = WinningPercentageCalculation("Team A", None)
    assert calc.calculate(matches) == 0.5  # 0 wins, 3 draws


def test_winning_percentage_calculation_no_matches():
    matches = []
    calc = WinningPercentageCalculation("Team A", None)
    assert calc.calculate(matches) == 0.0


def test_winning_percentage_calculation_skip_team_name(matches):
    calc = WinningPercentageCalculation("Team A", "Team B")
    assert (
        calc.calculate(matches) == 0.75
    )  # 2 wins, 1 draw, 1 loss (skipping matches with Team B)


def test_winning_percentage_calculation_rounding(teams):
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team C", 2, 1),
        Match("Team A", "Team D", 1, 1),  # Draw
    ]
    calc = WinningPercentageCalculation("Team A", None, number_of_digits=3)
    assert calc.calculate(matches) == 0.833  # 2 wins, 1 draw


def test_opponents_winning_percentage_calculation_no_team_name():
    """
    Test the calculation when no team name is provided.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team C", 2, 1),
        Match("Team D", "Team E", 1, 1),
    ]
    calc = OpponentsWinningPercentageCalculation(None, None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.0


def test_opponents_winning_percentage_calculation_empty_team_name():
    """
    Test the calculation when an empty team name is provided.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team C", 2, 1),
        Match("Team D", "Team E", 1, 1),
    ]
    calc = OpponentsWinningPercentageCalculation("", None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.0


def test_opponents_winning_percentage_calculation_all_wins():
    """
    Test the calculation for a team that wins all matches.
    """
    # Arrange
    matches = [
        Match("Team E", "Team F", 3, 0),
        Match("Team E", "Team G", 2, 1),
        Match("Team F", "Team H", 1, 1),
        Match("Team G", "Team H", 0, 2),
    ]
    calc = OpponentsWinningPercentageCalculation("Team E", None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.25  # Opponents: Team F (0.0), Team G (1.0)


def test_opponents_winning_percentage_calculation_all_losses():
    """
    Test the calculation for a team that loses all matches.
    """
    # Arrange
    matches = [
        Match("Team F", "Team H", 0, 2),
        Match("Team F", "Team I", 1, 3),
        Match("Team H", "Team I", 2, 2),
        Match("Team G", "Team H", 0, 2),
    ]
    calc = OpponentsWinningPercentageCalculation("Team F", None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.62  # Opponents: Team H (0.5), Team I (0.5)


def test_opponents_winning_percentage_calculation_no_matches():
    """
    Test the calculation when there are no matches.
    """
    # Arrange
    matches = []
    calc = OpponentsWinningPercentageCalculation("Team A", None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.0


def test_opponents_winning_percentage_calculation_skip_team_name():
    """
    Test the calculation when skipping a specific team.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team C", 2, 1),
        Match("Team A", "Team D", 1, 1),
        Match("Team B", "Team C", 0, 2),
        Match("Team C", "Team D", 1, 1),
    ]
    calc = OpponentsWinningPercentageCalculation("Team A", "Team B")

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.42  # Opponents: Team C (1.0), Team D (0.5)


def test_opponents_winning_percentage_calculation_rounding():
    """
    Test the calculation with rounding to a specified number of digits.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team C", 2, 1),
        Match("Team A", "Team D", 1, 1),  # Draw
        Match("Team B", "Team C", 0, 2),
        Match("Team C", "Team D", 1, 1),
    ]
    calc = OpponentsWinningPercentageCalculation("Team A", None, number_of_digits=3)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.417  # Opponents: Team B (1.0), Team C (1.0), Team D (0.5)


def test_opponents_winning_percentage_calculation_multiple_games():
    """
    Test the calculation when Team A plays multiple games against an opponent.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team A", "Team B", 2, 1),
        Match("Team A", "Team C", 1, 1),
        Match("Team B", "Team C", 0, 2),
        Match("Team C", "Team D", 1, 1),
    ]
    calc = OpponentsWinningPercentageCalculation("Team A", None)

    # Act
    result = calc.calculate(matches)

    # Assert
    assert result == 0.25  # Opponents: Team B (1.0), Team C (0.5)
