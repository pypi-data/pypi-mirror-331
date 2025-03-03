import pytest
from datetime import date, time
from src.jk_soccer_core.models.match import Match
from src.jk_soccer_core.match import (
    MatchDecorator,
    get_team_names,
    opponent_names_generator,
)


@pytest.fixture
def sample_match():
    """
    Fixture for creating a sample match.
    """
    return Match(
        home_team="Team A",
        away_team="Team B",
        home_score=2,
        away_score=2,
        date=date(2023, 5, 15),
        time=time(15, 30),
        penalty_shootout=False,
    )


def test_match_decorator_properties(sample_match):
    """
    Test the properties of the MatchDecorator.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    match = decorator.match
    is_draw = decorator.is_draw
    winner = decorator.winner
    loser = decorator.loser

    # Assert
    assert match == sample_match
    assert is_draw is True
    assert winner is None
    assert loser is None


def test_match_decorator_winner_loser_team_a_wins():
    """
    Test the winner and loser properties when Team A wins.
    """
    # Arrange
    match = Match(home_team="Team A", away_team="Team B", home_score=3, away_score=1)
    decorator = MatchDecorator(match)

    # Act
    winner = decorator.winner
    loser = decorator.loser

    # Assert
    assert winner == "Team A"
    assert loser == "Team B"


def test_match_decorator_winner_loser_team_b_wins():
    """
    Test the winner and loser properties when Team B wins.
    """
    # Arrange
    match = Match(home_team="Team A", away_team="Team B", home_score=1, away_score=3)
    decorator = MatchDecorator(match)

    # Act
    winner = decorator.winner
    loser = decorator.loser

    # Assert
    assert winner == "Team B"
    assert loser == "Team A"


def test_match_decorator_winner_loser_draw():
    """
    Test the winner and loser properties when the match is a draw.
    """
    # Arrange
    match = Match(home_team="Team A", away_team="Team B", home_score=2, away_score=2)
    decorator = MatchDecorator(match)

    # Act
    winner = decorator.winner
    loser = decorator.loser

    # Assert
    assert winner is None
    assert loser is None


def test_match_decorator_has_team_name_team_a(sample_match):
    """
    Test if the match contains Team A.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    result = decorator.has_team_name("Team A")

    # Assert
    assert result is True


def test_match_decorator_has_team_name_team_b(sample_match):
    """
    Test if the match contains Team B.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    result = decorator.has_team_name("Team B")

    # Assert
    assert result is True


def test_match_decorator_has_team_name_team_c(sample_match):
    """
    Test if the match contains Team C.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    result = decorator.has_team_name("Team C")

    # Assert
    assert result is False


def test_match_decorator_get_opponent_name_team_a(sample_match):
    """
    Test getting the opponent name for Team A.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    opponent_name = decorator.get_opponent_name("Team A")

    # Assert
    assert opponent_name == "Team B"


def test_match_decorator_get_opponent_name_team_b(sample_match):
    """
    Test getting the opponent name for Team B.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    opponent_name = decorator.get_opponent_name("Team B")

    # Assert
    assert opponent_name == "Team A"


def test_match_decorator_get_opponent_name_team_c(sample_match):
    """
    Test getting the opponent name for Team C.
    """
    # Arrange
    decorator = MatchDecorator(sample_match)

    # Act
    opponent_name = decorator.get_opponent_name("Team C")

    # Assert
    assert opponent_name is None


def test_get_team_names():
    """
    Test getting the names of the teams in the matches.
    """
    # Arrange
    matches = [
        Match(home_team="Team A", away_team="Team B"),
        Match(home_team="Team C", away_team="Team D"),
        Match(home_team="Team A", away_team="Team C"),
    ]

    # Act
    team_names = get_team_names(matches)

    # Assert
    assert set(team_names) == {"Team A", "Team B", "Team C", "Team D"}


@pytest.mark.parametrize(
    "home_team, away_team, home_score, away_score, team_name, expected_won",
    [
        ("Team A", "Team B", 3, 1, "Team A", True),  # Team A wins
        ("Team A", "Team B", 1, 3, "Team B", True),  # Team B wins
        ("Team A", "Team B", 2, 2, "Team A", False),  # Draw
        ("Team A", "Team B", 2, 2, "Team B", False),  # Draw
        ("", "Team B", 3, 1, "", True),  # Empty home team name wins
        ("Team A", "", 3, 1, "", False),  # Empty away team name loses
        (None, "Team B", 3, 1, None, False),  # None home team name
        ("Team A", None, 3, 1, None, False),  # None away team name
        (" ", "Team B", 3, 1, " ", True),  # Space as home team name wins
        ("Team A", " ", 3, 1, " ", False),  # Space as away team name loses
    ],
)
def test_match_decorator_won(
    home_team, away_team, home_score, away_score, team_name, expected_won
):
    """
    Test the won method of the MatchDecorator.
    """
    # Arrange
    match = Match(
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
    )
    decorator = MatchDecorator(match)

    # Act
    won = decorator.won(team_name)

    # Assert
    assert won == expected_won, f"Expected won {expected_won}, but got {won}"


@pytest.mark.parametrize(
    "home_team, away_team, home_score, away_score, team_name, expected_lost",
    [
        ("Team A", "Team B", 3, 1, "Team B", True),  # Team B loses
        ("Team A", "Team B", 1, 3, "Team A", True),  # Team A loses
        ("Team A", "Team B", 2, 2, "Team A", False),  # Draw
        ("Team A", "Team B", 2, 2, "Team B", False),  # Draw
        ("Team A", "Team B", 2, 2, None, False),  # Draw with None team name
        ("", "Team B", 3, 1, "Team B", True),  # Empty home team name wins
        ("Team A", "", 3, 1, "Team A", False),  # Empty away team name loses
        (None, "Team B", 3, 1, "Team B", True),  # None home team name
        ("Team A", None, 3, 1, "Team A", False),  # None away team name
        (" ", "Team B", 3, 1, "Team B", True),  # Space as home team name wins
        ("Team A", " ", 3, 1, "Team A", False),  # Space as away team name loses
    ],
)
def test_match_decorator_lost(
    home_team, away_team, home_score, away_score, team_name, expected_lost
):
    """
    Test the lost method of the MatchDecorator.
    """
    # Arrange
    match = Match(
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score,
    )
    decorator = MatchDecorator(match)

    # Act
    lost = decorator.lost(team_name)

    # Assert
    assert lost == expected_lost, f"Expected lost {expected_lost}, but got {lost}"


def test_opponent_names_generator_with_none_name():
    """
    Test the opponent_names_generator function when a name is None.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team C", "Team D", 2, 1),
        Match("Team E", None, 1, 1),
    ]

    # Act
    result = list(opponent_names_generator(None, matches))

    # Assert
    assert result == []


def test_opponent_names_generator_with_none_opponent_name():
    """
    Test the opponent_names_generator function when an opponent's name is None.
    """
    # Arrange
    matches = [
        Match("Team A", "Team B", 1, 0),
        Match("Team C", "Team D", 2, 1),
        Match("Team E", None, 1, 1),
    ]

    # Act
    result = list(opponent_names_generator("Team E", matches))

    # Assert
    assert result == []
