"""Controller-only navigation/combat helpers for the actual native GBA game.

Pathfinding observes the matching ELF's collision/trigger/enemy arrays. Every
movement and battle action goes through Mgba.step/tap. There is no warp, memory
write, quest-flag write, or savedata restoration operation.
"""
from __future__ import annotations
from dataclasses import dataclass
import heapq
import itertools
import struct


@dataclass(frozen=True)
class Enemy:
    index: int
    x: int
    y: int
    type: int
    hp: int
    maxhp: int
    damage: int
    active: int
    elite: int


class Navigator:
    def __init__(self, emu):
        self.emu = emu
        for name in ("collision", "trigger", "enemies", "current_world", "current_room", "current_layer"):
            if name not in emu.symbols:
                raise KeyError(f"Matching native ELF is missing required symbol: {name}")
        if emu.symbols["collision"].size != 4096 or emu.symbols["trigger"].size != 4096:
            raise ValueError("Expected the native 64x64 collision and trigger arrays")

    def value(self, name):
        return self.emu.read_symbol(name)

    def position(self):
        if "player" in self.emu.symbols:
            return (self.emu.read_symbol("player", width=2, signed=True),
                    self.emu.read_symbol("player", width=2, offset=2, signed=True))
        return (self.emu.read_symbol("player.0", signed=True), self.emu.read_symbol("player.1", signed=True))

    def location(self):
        return tuple(self.value(name) for name in ("current_world", "current_room", "current_layer"))

    def board(self):
        return self.emu.read_range(self.emu.symbols["collision"].address, 4096)

    def triggers(self):
        return self.emu.read_range(self.emu.symbols["trigger"].address, 4096)

    @staticmethod
    def can_stand(board, x, y, *, avoid_hazards=True):
        # Same four +/-5px footprint corners as the actual game movement code.
        if not (8 <= x <= 503 and 8 <= y <= 503):
            return False
        for px, py in ((x - 5, y - 5), (x + 5, y - 5), (x - 5, y + 5), (x + 5, y + 5)):
            if board[(py >> 3) * 64 + (px >> 3)] == 1:
                return False
        return not avoid_hazards or board[(y >> 3) * 64 + (x >> 3)] != 2

    @staticmethod
    def nearby_trigger(triggers, x, y):
        tx, ty = x >> 3, y >> 3
        for sy in range(ty - 1, ty + 2):
            for sx in range(tx - 1, tx + 2):
                if 0 <= sx < 64 and 0 <= sy < 64:
                    value = triggers[sy * 64 + sx]
                    if value:
                        return value, (sx, sy)
        return 0, None

    def _path(self, board, start, goals, *, avoid_hazards=True):
        """A* on the actual two-pixel walking lattice; no tile-width guesses."""
        goals = set(goals)
        if not goals:
            raise RuntimeError("No controller-reachable goal positions exist in the native collision map")
        minx, maxx = min(p[0] for p in goals), max(p[0] for p in goals)
        miny, maxy = min(p[1] for p in goals), max(p[1] for p in goals)
        def heuristic(point):
            x, y = point
            return (max(minx - x, 0, x - maxx) + max(miny - y, 0, y - maxy)) // 2
        counter = itertools.count()
        queue = [(heuristic(start), next(counter), 0, start)]
        cost, previous = {start: 0}, {}
        passable = {}
        while queue:
            _estimate, _order, length, point = heapq.heappop(queue)
            if length != cost[point]:
                continue
            if point in goals:
                result = [point]
                while point in previous:
                    point = previous[point]
                    result.append(point)
                return list(reversed(result))
            x, y = point
            for candidate in ((x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)):
                if candidate not in passable:
                    passable[candidate] = self.can_stand(board, *candidate, avoid_hazards=avoid_hazards)
                if not passable[candidate]:
                    continue
                distance = length + 1
                if distance < cost.get(candidate, 1 << 30):
                    cost[candidate] = distance
                    previous[candidate] = point
                    heapq.heappush(queue, (distance + heuristic(candidate), next(counter), distance, candidate))
        raise RuntimeError(f"No physical controller path from {start} to {len(goals)} goals at location {self.location()}")

    def _surface(self):
        if self.value("intro") or self.value("v10_opening") or self.value("game_mode") != 0:
            raise RuntimeError("Navigation requires a live surface after title/opening")
        if self.value("cinema_active"):
            raise RuntimeError("Finish the visible native cinema before walking")
        if self.value("npc_dialogue_active") or self.value("shop_open"):
            raise RuntimeError("Close native conversation/shop before walking")
        for name in ("riddle_open", "pending_choice", "v10_hw_riddle", "v10_realm_riddle",
                     "arc_pending", "g6_pending", "g7_pending"):
            if name in self.emu.symbols and self.value(name):
                raise RuntimeError(f"Resolve the native choice {name} before walking")

    @staticmethod
    def _waypoints(path):
        if len(path) < 2:
            return []
        result, direction = [], None
        for prior, point in zip(path, path[1:]):
            current = (point[0] - prior[0], point[1] - prior[1])
            if direction is not None and current != direction:
                result.append(prior)
            direction = current
        result.append(path[-1])
        return result

    def _walk(self, goal_factory, *, avoid_hazards=True, max_frames=12000):
        self._surface()
        location = self.location()
        begin = self.emu.frame
        stalled = 0
        for _replan in range(40):
            board = self.board()
            start = self.position()
            goals = goal_factory(start, board)
            if start in goals:
                self.emu.step((), 2)
                return self.position()
            path = self._path(board, start, goals, avoid_hazards=avoid_hazards)
            displaced = False
            for target in self._waypoints(path):
                while self.position() != target:
                    self._surface()
                    if self.location() != location:
                        raise RuntimeError("Native location changed during walking")
                    if self.emu.frame - begin >= max_frames:
                        raise RuntimeError(f"Walking input budget exceeded at {self.position()}, target={target}")
                    before = self.position()
                    dx, dy = target[0] - before[0], target[1] - before[1]
                    if dx and dy:
                        # A real enemy knockback or odd-coordinate drift moved
                        # the actor off the planned segment; read and replan.
                        displaced = True
                        break
                    distance = abs(dx or dy)
                    key = "RIGHT" if dx > 0 else "LEFT" if dx < 0 else "DOWN" if dy > 0 else "UP"
                    frames = max(1, min(8, distance // 4))
                    self.emu.step(key, frames)
                    after = self.position()
                    stalled = stalled + frames if after == before else 0
                    if stalled >= 180:
                        raise RuntimeError(f"Real controller motion stalled at {after} toward {target}")
                    if ((dx and abs(target[0] - after[0]) > abs(dx)) or
                            (dy and abs(target[1] - after[1]) > abs(dy))):
                        displaced = True
                        break
                if displaced:
                    break
            if not displaced:
                self.emu.step((), 2)
                return self.position()
        raise RuntimeError("Native actor was displaced too often for navigation")

    def walk_to(self, x, y, *, tolerance=4, avoid_hazards=True, max_frames=12000):
        """Walk using normal direction keys to a nearby passable position."""
        def goals(start, board):
            parity_x, parity_y = start[0] % 2, start[1] % 2
            return {(px, py) for px in range(max(8, x - tolerance), min(503, x + tolerance) + 1)
                    for py in range(max(8, y - tolerance), min(503, y + tolerance) + 1)
                    if px % 2 == parity_x and py % 2 == parity_y
                    and abs(px - x) + abs(py - y) <= tolerance
                    and self.can_stand(board, px, py, avoid_hazards=avoid_hazards)}
        return self._walk(goals, avoid_hazards=avoid_hazards, max_frames=max_frames)

    def goto_trigger(self, value, *, at=None, avoid_hazards=True, max_frames=12000):
        """Walk until the game's own scan selects this trigger and tile."""
        triggers = self.triggers()
        tiles = {(i % 64, i // 64) for i, trigger in enumerate(triggers) if trigger == value}
        if at is not None:
            if tuple(at) not in tiles:
                raise RuntimeError(f"Native trigger {value} is absent at {at} in {self.location()}")
            tiles = {tuple(at)}
        if not tiles:
            raise RuntimeError(f"Native trigger {value} is absent in {self.location()}")
        def goals(start, board):
            result = set()
            for tx, ty in tiles:
                for px in range(max(8, (tx - 1) * 8), min(504, (tx + 2) * 8)):
                    for py in range(max(8, (ty - 1) * 8), min(504, (ty + 2) * 8)):
                        if px % 2 != start[0] % 2 or py % 2 != start[1] % 2:
                            continue
                        selected, tile = self.nearby_trigger(triggers, px, py)
                        if selected == value and tile in tiles and self.can_stand(board, px, py, avoid_hazards=avoid_hazards):
                            result.add((px, py))
            return result
        result = self._walk(goals, avoid_hazards=avoid_hazards, max_frames=max_frames)
        selected, tile = self.nearby_trigger(self.triggers(), *result)
        if selected != value or tile not in tiles:
            raise RuntimeError("Native trigger changed before the controller reached it")
        self.emu._event("trigger_reached", frame=self.emu.frame, location=self.location(), trigger=value,
                        tile=tile, actual_position=result)
        return result

    def interact(self, value, *, at=None, hold=12, release=12, **navigation):
        self.goto_trigger(value, at=at, **navigation)
        self.emu.tap("A", hold=hold, release=release)
        return self.location()

    def enemies(self):
        symbol = self.emu.symbols["enemies"]
        if symbol.size != 160:
            raise ValueError("Enemy array layout changed; expected ten native 16-byte Enemy entries")
        data = self.emu.read_range(symbol.address, symbol.size)
        result = []
        for index in range(10):
            offset = index * 16
            x, y = struct.unpack_from("<hh", data, offset)
            result.append(Enemy(index, x, y, data[offset + 6], data[offset + 7], data[offset + 8],
                                data[offset + 9], data[offset + 10], data[offset + 12]))
        return result

    def battle(self, *, max_frames=30000):
        """Win the live menu battle using ATTACK and timed B blocking."""
        if self.value("game_mode") != 3:
            raise RuntimeError("No actual native battle is running")
        begin = self.emu.frame
        index = self.value("battle_index")
        kills_before = self.value("kill_count")
        while self.value("game_mode") == 3:
            if self.emu.frame - begin >= max_frames:
                raise RuntimeError("Controller battle exceeded its input budget")
            phase = self.value("battle_phase")
            if phase == 0:
                cursor = self.value("battle_cursor")
                if cursor & 1:
                    self.emu.tap("LEFT", hold=4, release=4)
                for _ in range(3):
                    if self.value("battle_cursor") == 0:
                        break
                    self.emu.tap("UP", hold=4, release=4)
                if self.value("battle_cursor") != 0:
                    raise RuntimeError("Actual ATTACK menu selection failed")
                self.emu.tap("A", hold=4, release=4)
            elif phase == 1:
                # B is pressed while the enemy's telegraphed attack phase is
                # active. It is not used in command phase, where B means FLEE.
                self.emu.tap("B", hold=4, release=2)
            else:
                self.emu.step((), 4)
        enemy = self.enemies()[index]
        kills_after = self.value("kill_count")
        if enemy.active or kills_after <= kills_before:
            raise RuntimeError("Controller battle ended without a native kill; do not count it as a victory")
        self.emu._event("controller_battle_won", frame=self.emu.frame, location=self.location(), enemy_index=index,
                        kill_count_before=kills_before, kill_count_after=kills_after)
        return index

    def fight_enemy(self, index):
        """Walk near an observed enemy, use actual A+SELECT, then fight."""
        for _attempt in range(12):
            enemy = self.enemies()[index]
            if not enemy.active:
                return
            self.walk_to(enemy.x, enemy.y, tolerance=26)
            enemy = self.enemies()[index]
            x, y = self.position()
            if abs(x - enemy.x) + abs(y - enemy.y) >= 46:
                continue
            self.emu.tap(("A", "SELECT"), hold=8, release=4)
            if self.value("game_mode") != 3:
                raise RuntimeError("Actual A+SELECT controller input did not enter a battle")
            self.battle()
        if self.enemies()[index].active:
            raise RuntimeError(f"Could not reach and defeat actual enemy {index}")

    def wait_cinema(self, *, max_frames=1200):
        """Let timed native cinema play; never starts or mutates a scene."""
        begin = self.emu.frame
        while self.value("cinema_active"):
            if self.emu.frame - begin >= max_frames:
                raise RuntimeError("Visible native cinema is still active; its controller continuation is required")
            self.emu.step((), 8)

    def save_menu(self):
        self._surface()
        self.emu.tap("START", hold=12, release=12)
        if self.value("game_mode") != 2:
            raise RuntimeError("START did not open the actual pause menu")
        for _ in range(9):
            self.emu.tap("DOWN", hold=12, release=12)
        if self.value("pause_sel") != 9:
            raise RuntimeError("Actual SAVE menu row was not selected")
        self.emu.tap("A", hold=12, release=12)
        if self.value("pause_page") != 10:
            raise RuntimeError("Actual SAVE menu action did not finish")
        self.emu.tap("B", hold=12, release=12)
        self.emu.tap("B", hold=12, release=12)
        self._surface()
