Requirements specification
==========================

Server API
----------
1. Works with websocket and uses inly 3 requests:
   1. `init` - Initialize new game.
   2. `state` - Getting state. Just returns current game state.
   3. `open` - Opening a card. It triggers scores recalculation and winner detection.

2. Game rules - Rules(BaseModel):
   1. Cards set.
   2. Field size.
   3. Teams count.
   4. Cards count for each team.
   5. Black cards count.

3. Game state from server. This data returned by both `open` and `state` requests. It contains:
   1. Cards data.
   2. Team scores.
      1. Recalculatig on opening card.
   3. Winner.
      1. Team when it reaches 0 point.
      2. Black team if black card exists and they are opened.
      3. Calculatig on opening card only if there was no winner.

Client
------

1. Player:
   1. Can turn cards.
   2. Sees team of turned cards only.
   3. Turning cards on active game requires server response.
   4. Turning cards when game ended does not require server.

2. Captan:
   1. Can't turn cards
   2. Sees all cards

3. Common:
   1. Scores calculated on server not locally.
   2. Winner determined on server not locally.
   3. LocalStorage data:
      1. Font size.
      2. BW or Color.
      3. View rotation.
   4. Ending game leads to socked disconnect.


   
