from typing import Iterable, Optional
from .abstract_match_calculation import AbstractMatchCalculation
from jk_soccer_core import Match, MatchDecorator
from jk_soccer_core.match import matches_played_generator


class PointsCalculation(AbstractMatchCalculation):
    """
    Calculate the number of points a team has earned in an iterable of matches.
    """

    def __init__(self, team_name: Optional[str], skip_team_name: Optional[str] = None):
        self.__team_name = team_name
        self.__skip_team_name = skip_team_name

    def calculate(self, matches: Iterable[Match]) -> int:
        """
        Calculate the number of points a team has earned in a list of matches.

        In a match a team earns 1 point if the match is a draw, 0 points if the team lost, and 3 points if the team won.

        :param team_name: The name of the team to calculate the points for.
        :param matches: A list of matches to calculate the points from.
        :return: The number of points the team has earned.
        """
        if not self.__team_name:
            return 0

        points = 0
        for match in matches_played_generator(
            self.__team_name, matches, self.__skip_team_name
        ):
            decorated_match = MatchDecorator(match)
            points += 1 if decorated_match.is_draw else 0
            points += 3 if decorated_match.won(self.__team_name) else 0

        return points
