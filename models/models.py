"""
All object models
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal, TypedDict


class Board(TypedDict):
    """
    Board class
    """

    a: Annotated[list[str], 3]
    b: Annotated[list[str], 3]
    c: Annotated[list[str], 3]


@dataclass
class Player:
    """
    Player class
    """

    game: Game
    player_id: str
    name: str
    number: Literal[1, 2]
    symbol: str
    score: int = 0
    is_ai: bool = False
    created_at: datetime


@dataclass
class Game:
    """
    Game class
    """

    game_id: str
    room: Room
    name: str
    number: int
    players: list[Player] = []
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
    all_players: list[Player] = []
    lost_players: list[Player] = []
    games: dict[str, Game] = {}


# 	bracket # idk what this would be
