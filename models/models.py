# help, how do i typehint this
#pylint: disable=too-many-instance-attributes
"""
All object models
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Player:
    """
    Player class
    """

    game: str#Game
    name: str
    number: int
    symbol: str
    score: int = 0
    is_ai: bool = False
    created_at: str


@dataclass
class Game:
    """
    Game class
    """

    game_id: str
    room: str#Room
    name: str
    number: int
    players: List[Player] = []
    turn: bool = False
    ended: bool = False
    tie: bool = False
    ai_game: bool = False
    created_at: str


@dataclass
class Room:
    """
    Room class
    """

    room_id: str
    name: str
    all_players: List[Player] = []
    lost_players: List[Player] = []
    games: Dict[Game] = {}


# 	bracket # idk what this would be
