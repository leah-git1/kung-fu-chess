"""
GameSession — authoritative game loop for one match.

Responsibilities:
- Own the Game instance and advance time each tick.
- Receive MOVE / JUMP commands from players and apply them.
- Broadcast STATE_UPDATE every 200ms as a sync snapshot (reduced from every tick).
- Detect game-over, update ratings, broadcast GameOverMsg.
"""
from __future__ import annotations
import asyncio
import json
import sys, os

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "logic"))
sys.path.insert(0, _ROOT)

from game.game import Game
from board.board_parser import BoardParser

from shared.constants import TICK_RATE_MS
from shared.messages import StateUpdateMsg, GameOverMsg, ErrorMsg, MoveAckMsg, JumpAckMsg, parse

from server.session.player_connection import PlayerConnection
from server.protocol.serializer import board_to_json, motions_to_json, apply_move, apply_jump, cooldowns_to_json
from server.logging.server_logger import log
from server.rating import rating_service

_STATE_UPDATE_INTERVAL_MS = 200

_STARTING_POSITION = """\
Board:
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
Commands:"""


class GameSession:
    def __init__(self, white: PlayerConnection, black: PlayerConnection, on_done=None):
        self._players: dict[str, PlayerConnection] = {"w": white, "b": black}
        self._on_done = on_done
        board = BoardParser().parse(_STARTING_POSITION.splitlines())
        self._game = Game(board)
        self._game_over_sent  = False
        self._ms_since_update = 0

    async def run(self) -> None:
        log(f"session started  w={self._players['w'].name}  b={self._players['b'].name}")
        try:
            await asyncio.gather(
                self._tick_loop(),
                self._receive_loop("w"),
                self._receive_loop("b"),
            )
        finally:
            if self._on_done:
                self._on_done()

    async def _tick_loop(self) -> None:
        interval = TICK_RATE_MS / 1000
        while not self._game_over_sent:
            await asyncio.sleep(interval)
            self._game.advance_time(TICK_RATE_MS)

            if self._game.game_over:
                self._game_over_sent = True
                winner = self._game.winner_color
                loser  = "b" if winner == "w" else "w"
                rating_service.apply_game_result(
                    self._players[winner].name,
                    self._players[loser].name,
                )
                await self._broadcast(GameOverMsg(winner=winner, reason="king captured"))
                log(f"game over — winner: {winner}")
                return

            self._ms_since_update += TICK_RATE_MS
            if self._ms_since_update >= _STATE_UPDATE_INTERVAL_MS:
                self._ms_since_update = 0
                await self._broadcast(StateUpdateMsg(
                    board=board_to_json(self._game),
                    time_ms=self._game.current_time,
                    motions={
                        **motions_to_json(self._game),
                        "cooldowns": cooldowns_to_json(self._game),
                    },
                ))

    async def _receive_loop(self, color: str) -> None:
        conn = self._players[color]
        try:
            async for raw in conn.websocket:
                if self._game_over_sent:
                    break
                try:
                    msg = parse(json.loads(raw))
                except (ValueError, KeyError) as e:
                    await conn.send(ErrorMsg(reason=str(e)))
                    continue
                await self._handle(color, msg)
        except Exception:
            pass

    async def _handle(self, color: str, msg) -> None:
        conn = self._players[color]
        if msg.__class__.__name__ == "MoveMsg":
            from_cell = tuple(msg.from_cell)
            piece = self._game.get_piece_at(from_cell)
            if piece is None or piece.color != color:
                await conn.send(ErrorMsg(reason="not your piece"))
                return
            if apply_move(msg, self._game):
                await self._broadcast(MoveAckMsg(
                    from_cell=list(from_cell),
                    to_cell=list(msg.to_cell),
                    time_ms=self._game.current_time,
                ))
        elif msg.__class__.__name__ == "JumpMsg":
            cell = tuple(msg.cell)
            piece = self._game.get_piece_at(cell)
            if piece is None or piece.color != color:
                await conn.send(ErrorMsg(reason="not your piece"))
                return
            if apply_jump(msg, self._game):
                await self._broadcast(JumpAckMsg(
                    cell=list(cell),
                    time_ms=self._game.current_time,
                ))

    async def _broadcast(self, msg) -> None:
        for conn in self._players.values():
            try:
                await conn.send(msg)
            except Exception:
                pass
