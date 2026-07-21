"""
BoardMirror — client-side view model of the authoritative server board.

Depends only on:
  - shared/  (wire protocol)
  - client/network/piece_vm.py  (own ViewModel)

Zero imports from logic/.
"""
from __future__ import annotations
from client.network.piece_vm import PieceVM
from shared.constants import JUMP_DURATION, LONG_REST_DURATION, SHORT_REST_DURATION


# ── motion view models ────────────────────────────────────────────────────────

class MoveMotionVM:
    def __init__(self, piece_vm, origin, destination, actual_destination, start_time, finish_time):
        self.piece              = piece_vm
        self.origin             = tuple(origin)
        self.destination        = tuple(destination)
        self.actual_destination = tuple(actual_destination)
        self.start_time         = start_time
        self.finish_time        = finish_time


class JumpMotionVM:
    def __init__(self, piece_vm, cell, finish_time):
        self.piece       = piece_vm
        self.cell        = tuple(cell)
        self.finish_time = finish_time


class CooldownVM:
    def __init__(self, piece_vm, rest_type, start_time, finish_time):
        self.piece       = piece_vm
        self.rest_type   = rest_type
        self.start_time  = start_time
        self.finish_time = finish_time


# ── mirror ────────────────────────────────────────────────────────────────────

class BoardMirror:
    ROWS = 8
    COLS = 8

    def __init__(self, on_capture=None):
        self.current_time: int        = 0
        self.game_over: bool          = False
        self.winner_color: str | None = None
        self._on_capture              = on_capture  # callable(piece_vm, cell, time_ms, by_color)

        self._grid: list[list]        = [[None] * self.COLS for _ in range(self.ROWS)]

        # (row, col) -> PieceVM  — one stable object per cell, reused as long as
        # the same sprite_key occupies that cell.  When a piece moves, the old
        # cell entry is removed and a new one is created at the destination.
        self._cell_registry: dict[tuple, PieceVM] = {}

        # keyed motion VMs — preserved across snapshots
        self._move_vms: dict[tuple, MoveMotionVM] = {}   # (key, origin, dest)
        self._jump_vms: dict[tuple, JumpMotionVM] = {}   # (key, cell)
        self._cd_vms:   dict[tuple, CooldownVM]   = {}   # (key, rest_type, finish_time)

    # ── piece identity ────────────────────────────────────────────────────────

    def _get_or_create(self, sprite_key: str, row: int, col: int) -> PieceVM:
        """Return the stable PieceVM for this cell, creating one if needed.
        If the cell already holds a different piece type, replace it."""
        cell = (row, col)
        vm = self._cell_registry.get(cell)
        if vm is None or vm.sprite_key != sprite_key:
            vm = PieceVM(sprite_key=sprite_key, state_name="idle")
            self._cell_registry[cell] = vm
        return vm

    # ── main update ───────────────────────────────────────────────────────────

    def apply_state_update(self, board: list, time_ms: int, motions: dict = None) -> None:
        self.current_time = time_ms
        motions = motions or {"moves": [], "jumps": [], "cooldowns": []}

        # ── rebuild grid with cell-stable PieceVM objects ─────────────────────
        new_grid = [[None] * self.COLS for _ in range(self.ROWS)]
        occupied: set[tuple] = set()

        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell is None:
                    continue
                key        = cell["k"] if isinstance(cell, dict) else cell
                state_name = cell.get("s", "idle") if isinstance(cell, dict) else "idle"
                vm = self._get_or_create(key, r, c)
                vm.state_name = state_name
                new_grid[r][c] = vm
                occupied.add((r, c))

        # evict registry entries for cells that are now empty
        for cell in list(self._cell_registry):
            if cell not in occupied:
                del self._cell_registry[cell]

        # ── capture detection ─────────────────────────────────────────────────
        if self._on_capture:
            for r in range(self.ROWS):
                for c in range(self.COLS):
                    old_vm = self._grid[r][c]
                    new_vm = new_grid[r][c]
                    if old_vm is not None and (new_vm is None or new_vm.sprite_key != old_vm.sprite_key):
                        by_color = new_vm.color if new_vm is not None else None
                        self._on_capture(old_vm, (r, c), time_ms, by_color)

        self._grid = new_grid

        # ── motion VMs — use registry for pieces still on grid, transient otherwise ──

        def _vm_for_motion(key: str, cell: tuple) -> PieceVM:
            """Get PieceVM for a motion — from registry if still on grid, else transient.
            Never writes into _cell_registry to avoid corrupting the grid."""
            existing = self._cell_registry.get(cell)
            if existing and existing.sprite_key == key:
                return existing
            return PieceVM(sprite_key=key, state_name="moving")

        # moves
        incoming_move_keys: set[tuple] = set()
        for m in motions.get("moves", []):
            stub_key = (m["key"], tuple(m["origin"]), tuple(m["destination"]))
            incoming_move_keys.add(stub_key)
            if stub_key not in self._move_vms:
                self._move_vms[stub_key] = MoveMotionVM(
                    piece_vm=_vm_for_motion(m["key"], tuple(m["origin"])),
                    origin=m["origin"],
                    destination=m["destination"],
                    actual_destination=m["actual_dest"],
                    start_time=m.get("start_time", m["finish_time"]),
                    finish_time=m["finish_time"],
                )
            else:
                self._move_vms[stub_key].actual_destination = tuple(m["actual_dest"])
        self._move_vms = {k: v for k, v in self._move_vms.items() if k in incoming_move_keys}

        # jumps
        incoming_jump_keys: set[tuple] = set()
        for m in motions.get("jumps", []):
            stub_key = (m["key"], tuple(m["cell"]))
            incoming_jump_keys.add(stub_key)
            if stub_key not in self._jump_vms:
                self._jump_vms[stub_key] = JumpMotionVM(
                    piece_vm=_vm_for_motion(m["key"], tuple(m["cell"])),
                    cell=m["cell"],
                    finish_time=m.get("finish_time", time_ms + JUMP_DURATION),
                )
        self._jump_vms = {k: v for k, v in self._jump_vms.items() if k in incoming_jump_keys}

        # cooldowns — cell is now provided by the server
        incoming_cd_keys: set[tuple] = set()
        for m in motions.get("cooldowns", []):
            stub_key = (m["key"], m["rest_type"], m["finish_time"])
            incoming_cd_keys.add(stub_key)
            if stub_key not in self._cd_vms:
                cell = tuple(m["cell"])
                vm = self._cell_registry.get(cell)
                if vm is None:
                    continue
                self._cd_vms[stub_key] = CooldownVM(
                    piece_vm=vm,
                    rest_type=m["rest_type"],
                    start_time=m["start_time"],
                    finish_time=m["finish_time"],
                )
        self._cd_vms = {k: v for k, v in self._cd_vms.items() if k in incoming_cd_keys}

    def apply_game_over(self, winner: str) -> None:
        self.game_over    = True
        self.winner_color = winner

    # ── interface expected by PieceRenderer ───────────────────────────────────

    def snapshot(self) -> list:
        return [row[:] for row in self._grid]

    def active_moves(self) -> list:
        return list(self._move_vms.values())

    def active_jumps(self) -> list:
        return list(self._jump_vms.values())

    def cooldown_progress(self, piece_vm) -> tuple | None:
        for cd in self._cd_vms.values():
            if cd.piece is piece_vm:
                duration = (LONG_REST_DURATION if cd.rest_type == "long"
                            else SHORT_REST_DURATION)
                elapsed  = duration - (cd.finish_time - self.current_time)
                progress = max(0.0, min(1.0, elapsed / duration))
                return progress, cd.rest_type
        return None

    def get_piece_at(self, cell: tuple) -> PieceVM | None:
        r, c = cell
        if not self.is_inside(cell):
            return None
        return self._grid[r][c]

    def is_inside(self, cell: tuple) -> bool:
        r, c = cell
        return 0 <= r < self.ROWS and 0 <= c < self.COLS
