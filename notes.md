- https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/
- look up jsonp

todo:
- secret for /game&user...?

- probably time to put everything in classes/objects
  - `Room`, `Game`, `Board`, `Player`, (?)`Bracket`

- BRACKETING FEATURE!!!! SINCE ROOMS EXIST!!!
  - or just switching out after each game based on who's participating
  - need an any-length list of playerPairs, and a 2-length list of currentPlayers, that way `not turn` won't break, and i can set `activePair` dynamically
  - MAKE A NEW BRANCH
  - make sure to identify active player list and already-lost list
    - no loser bracket, at least not for now for obvi reasons
  - cap room at maybe 16
  - either Ais or bys for gaps
  - "side 1 side 2"?
  - landing page per-room `/room` endpoint
  - `getRoom` has a list of games
    - `Room` can probably formatted as `games` is now
    - ```py
      rooms = {
        "roomId": {
          "name": "",
          "allPlayers": [],
          "lostPlayers": [],
          "games": {
            "gameId": {
              "name": "",
              "number": 0,#game number for something or other
              "players": [],
              "board": {},
              "turn": False,
              "ended": False,
              "tie": False,
              "ai": False
            }
          }
        }
      }
  - rooms are gonna need their own IDs lol
  - `/bracket?room=` (`View Bracket` button on room landing page)
  - `/game?room=_&user=`
  - allow users to spectate

- AI decision tree

- "upcoming features" page

- line through images when won...? just need 5 X/Os- blank, LTR, RTL, horizontal, vertical (or figure out how to draw a line on top of an image)

- suggestions page and/or button - just post and `open("suggestions", "a").write()`

- dark mode! 