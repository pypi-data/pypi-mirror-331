from typing import Optional, Iterable

from .models import Match


class MatchDecorator:
    """
    Decorator for the Match model
    """

    def __init__(self, match: Match):
        self.__match = match

    @property
    def match(self) -> Match:
        """
        Get the match
        """
        return self.__match

    @property
    def is_draw(self) -> bool:
        """
        Check if the match is a draw
        """
        return self.__match.home_score == self.__match.away_score

    @property
    def winner(self) -> Optional[str]:
        """
        Get the winning team
        """
        if self.__match.home_score > self.__match.away_score:
            return self.__match.home_team

        if self.__match.away_score > self.__match.home_score:
            return self.__match.away_team

        return None

    @property
    def loser(self) -> Optional[str]:
        """
        Get the losing team
        """
        if self.__match.home_score < self.__match.away_score:
            return self.__match.home_team

        if self.__match.away_score < self.__match.home_score:
            return self.__match.away_team

        return None

    def won(self, team_name: str) -> bool:
        """
        Check if the team won the match
        """
        if team_name is None:
            return False

        return self.winner == team_name

    def lost(self, team_name: str) -> bool:
        """
        Check if the team lost the match
        """
        if team_name is None:
            return False

        return self.loser == team_name

    def has_team_name(self, team_name: Optional[str]) -> bool:
        """
        Check if the match contains a specific team name
        """
        return (
            self.__match.home_team == team_name or self.__match.away_team == team_name
        )

    def get_opponent_name(self, target_team_name: str) -> Optional[str]:
        """
        Get the name of the opponent of a specific team
        """
        if not self.has_team_name(target_team_name):
            return None

        return (
            self.__match.home_team
            if self.__match.away_team == target_team_name
            else self.__match.away_team
        )


def get_team_names(matches: Iterable[Match]) -> Iterable[str]:
    """
    Get the names of the teams in the matches
    """
    team_names = list()

    for match in matches:
        if match.home_team not in team_names:
            team_names.append(match.home_team)

        if match.away_team not in team_names:
            team_names.append(match.away_team)

    return list(filter(None, team_names))  # Ensure no None values


def matches_played_generator(
    target_team_name: str,
    matches: Iterable[Match],
    skip_team_name: Optional[str] = None,
) -> Iterable[Match]:
    """
    Get the matches played by a specific team with an optional team to skip

    :param target_team_name: The name of the team to get the matches for
    :param matches: The matches to filter
    :param skip_team_name: The name of the team to skip
    :return: The matches played by the target team
    :rtype: Iterable[Match]
    """
    for match in matches:
        decorated_match = MatchDecorator(match)

        if not decorated_match.has_team_name(target_team_name):
            continue

        if skip_team_name and decorated_match.has_team_name(skip_team_name):
            continue

        yield match


def meetings_generator(
    team_name1: Optional[str], team_name2: Optional[str], matches: Iterable[Match]
) -> Iterable[Match]:
    """
    Get the matches between two teams
    """
    for match in matches:
        decorated_match = MatchDecorator(match)

        if not decorated_match.has_team_name(team_name1):
            continue

        if not decorated_match.has_team_name(team_name2):
            continue

        yield match


def opponent_names_generator(
    target_team_name: Optional[str], matches: Iterable[Match]
) -> Iterable[str]:
    """
    Get the names of the opponents of a specific team
    """
    if target_team_name is None:
        return

    for match in matches_played_generator(target_team_name, matches):
        opponent_name = MatchDecorator(match).get_opponent_name(target_team_name)

        if opponent_name is None:
            continue

        yield opponent_name
