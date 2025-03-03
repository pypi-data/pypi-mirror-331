from typing import Iterable, Optional
from .abstract_match_calculation import AbstractMatchCalculation
from jk_soccer_core import Match

from jk_soccer_core.match import opponent_names_generator, matches_played_generator
from jk_soccer_core.calculations.wins import WinsCalculation
from jk_soccer_core.calculations.losses import LossesCalculation
from jk_soccer_core.calculations.draws import DrawsCalculation


class WinningPercentageCalculation(AbstractMatchCalculation):
    """
    Calculate the winning percentage for a specific team
    """

    def __init__(
        self,
        team_name: Optional[str],
        skip_team_name: Optional[str] = None,
        number_of_digits: int = 2,
    ):
        self.__team_name = team_name
        self.__skip_team_name = skip_team_name
        self.__number_of_digits = number_of_digits

    def calculate(self, matches: Iterable[Match]) -> float:
        """
        Calculate the winning percentage for a specific team
        """
        if not self.__team_name:
            return 0.0

        filtered_matches = list(
            matches_played_generator(self.__team_name, matches, self.__skip_team_name)
        )
        wins = WinsCalculation(self.__team_name).calculate(filtered_matches)
        losses = LossesCalculation(self.__team_name).calculate(filtered_matches)
        draws = DrawsCalculation(self.__team_name).calculate(filtered_matches)
        matches_played = wins + losses + draws

        if matches_played == 0:
            return 0.0

        result = (float(wins) + (float(draws) / 2)) / float(matches_played)
        result = round(result, self.__number_of_digits)

        return result


class OpponentsWinningPercentageCalculation(AbstractMatchCalculation):
    """
    Calculate the average winning percentage of the opponents of a specific team

    The opponents winning percentage is calculated by summing the winning percentage of all the opponents of a specific team and dividing it by the number of opponents.
    """

    def __init__(
        self,
        team_name: Optional[str],
        skip_team_name: Optional[str] = None,
        number_of_digits: int = 2,
    ):
        self.__team_name = team_name
        self.__skip_team_name = skip_team_name
        self.__number_of_digits = number_of_digits

    def calculate(self, matches: Iterable[Match]) -> float:
        """
        Calculate the winning percentage of the opponents of a specific team
        """
        count = 0
        accumulator = 0.0
        for opponent_name in opponent_names_generator(self.__team_name, matches):
            # I need to calculate the winning percentage of the current opponent against teams other than the target team
            count += 1
            accumulator += WinningPercentageCalculation(
                opponent_name, self.__team_name, self.__number_of_digits
            ).calculate(matches)

        if count == 0:
            return 0.0

        return round(accumulator / float(count), self.__number_of_digits)
