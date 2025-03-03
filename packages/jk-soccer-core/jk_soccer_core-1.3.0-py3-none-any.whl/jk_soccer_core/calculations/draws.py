from typing import Iterable, Optional
from .abstract_match_calculation import AbstractMatchCalculation
from jk_soccer_core import Match, MatchDecorator
from jk_soccer_core.match import matches_played_generator


class DrawsCalculation(AbstractMatchCalculation):
    def __init__(self, team_name: Optional[str], skip_team_name: Optional[str] = None):
        self.__team_name = team_name
        self.__skip_team_name = skip_team_name

    def calculate(self, matches: Iterable[Match]) -> int:
        """
        Calculate the number of draws for a specific team.
        """
        if not self.__team_name:
            return 0

        return sum(
            1
            for match in matches_played_generator(
                self.__team_name, matches, self.__skip_team_name
            )
            if match.penalty_shootout or MatchDecorator(match).is_draw
        )
