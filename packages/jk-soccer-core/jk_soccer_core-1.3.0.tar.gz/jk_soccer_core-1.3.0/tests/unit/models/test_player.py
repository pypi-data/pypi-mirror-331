from jk_soccer_core.models import Player


def test_default_player() -> None:
    # Arrange

    # Act
    player = Player("Wilma Flintstone")

    # Assert
    assert len(player.__dict__) == 3, (
        f"Expected 2 attributes, but got {len(player.__dict__)}"
    )
    assert player.name == "Wilma Flintstone"
    assert player.position is None
