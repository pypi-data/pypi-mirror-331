from jk_soccer_core.models import Team, Coach, Player


def test_default_team() -> None:
    # Arrange

    # Act
    team = Team("Team A")

    # Assert
    assert len(team.__dict__) == 4, (
        f"Expected 4 attributes, but got {len(team.__dict__)}"
    )
    assert team.name == "Team A", f"Expected None, but got {team.name}"
    assert isinstance(team.coaches, list), f"Expected None, but got {team.coaches}"
    assert isinstance(team.players, list), f"Expected None, but got {team.players}"


def test_valid_team() -> None:
    # Arrange
    name = "The A Team"
    coaches = [Coach(name="John"), Coach(name="Jane")]
    players = [Player(name="Alice"), Player(name="Bob")]

    # Act
    team = Team(name=name, coaches=coaches, players=players)

    # Assert
    assert team.name == name, f"Expected {name}, but got {team.name}"
    assert team.coaches == coaches, f"Expected {coaches}, but got {team.coaches}"
    assert team.players == players, f"Expected {players}, but got {team.players}"
