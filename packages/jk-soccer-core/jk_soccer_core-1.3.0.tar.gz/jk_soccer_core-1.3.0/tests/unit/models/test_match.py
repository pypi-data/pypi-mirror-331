from datetime import date, time
from jk_soccer_core.models import Match


def test_default_match() -> None:
    # Arrange
    expected_date = date(1970, 1, 1)
    expected_time = time(0, 0, 0)

    # Act
    match = Match()

    # Assert
    assert len(match.__dict__) == 8, (
        f"Expected 7 attributes, but got {len(match.__dict__)}"
    )
    assert match.home_team is None, f"Expected None, but got {match.home_team}"
    assert match.away_team is None, f"Expected None, but got {match.away_team}"
    assert match.home_score == 0, f"Expected 0, but got {match.home_score}"
    assert match.away_score == 0, f"Expected 0, but got {match.away_score}"
    assert match.date == expected_date, (
        f"Expected {expected_date}, but got {match.date}"
    )
    assert match.time == expected_time, (
        f"Expected {expected_time}, but got {match.time}"
    )
    assert match.penalty_shootout is False, (
        f"Expected False, but got {match.penalty_shootout}"
    )
