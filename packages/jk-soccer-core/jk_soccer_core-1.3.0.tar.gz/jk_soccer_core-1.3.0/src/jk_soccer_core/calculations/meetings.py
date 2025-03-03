from typing import Iterable, Optional
from .abstract_match_calculation import AbstractMatchCalculation
from jk_soccer_core import Match
from jk_soccer_core.match import meetings_generator


class MeetingsCalculation(AbstractMatchCalculation):
    """
    Calculate the number of meetings between two teams.
    """

    def __init__(self, team_name1: Optional[str], team_name2: Optional[str]):
        self.__team_name1 = team_name1
        self.__team_name2 = team_name2

    def calculate(self, matches: Iterable[Match]) -> int:
        """
        Calculate the number of meetings between two teams.

        :param matches: The list of matches to analyze.
        :return: The number of meetings between the two teams.
        """
        return len(
            [
                _
                for _ in meetings_generator(
                    self.__team_name1, self.__team_name2, matches
                )
            ]
        )
