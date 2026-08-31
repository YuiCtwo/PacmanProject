from __future__ import annotations

import sys
import tkinter as tk

from typing import Iterable, List, Optional, Protocol, Sequence, Tuple, Set

from engine.core import GameState
from engine.layout import GameLayout
from utils.pos_utils import Position2D


class GameRenderer(Protocol):
    def render(self, game_stat: GameState) -> None: ...
    def close(self) -> None: ...


class ConsoleRenderer:
    def __init__(self, stream=None):
        self.stream = stream or sys.stdout

    def render(self, game_stat: GameState) -> None:
        board = []
        ghost_positions = set(game_stat.ghost_positions)

        for y in range(game_stat.layout.height - 1, -1, -1):
            row = []
            for x in range(game_stat.layout.width):
                pos = (x, y)
                if pos in game_stat.layout.walls:
                    row.append('%')
                elif pos == game_stat.pacman_position:
                    row.append('P')
                elif pos in ghost_positions:
                    row.append('G')
                elif pos in game_stat.layout.capsules:
                    row.append('o')
                elif pos in game_stat.layout.foods:
                    row.append('.')
                else:
                    row.append(' ')
            board.append(''.join(row))

        self.stream.write(f"Step: {game_stat.step_count}  Score: {game_stat.score:.1f}\n")
        self.stream.write('\n'.join(board))
        self.stream.write('\n')
        self.stream.flush()

    def close(self) -> None:
        if hasattr(self.stream, "flush"):
            self.stream.flush()


class GUIRenderer:
    def __init__(self, cell_size: int = 32, title: str = "Pacman"):
        self.cell_size = cell_size
        self.title = title
        self._root = None
        self._canvas = None
        self._cells = {}
        self._text_id = None
        self._layout = None
        self._tk = None

    def _ensure_window(self, layout: GameLayout) -> None:
        if self._root is not None and self._layout == layout:
            return

        self.close()
        self._tk = tk
        self._root = tk.Tk()
        self._root.title(self.title)
        width = layout.width * self.cell_size
        height = layout.height * self.cell_size + 32
        self._canvas = tk.Canvas(self._root, width=width, height=height, bg="black", highlightthickness=0)
        self._canvas.pack()
        self._layout = layout
        self._cells = {}
        self._text_id = None

    def _draw_static(self, layout: GameLayout) -> None:
        assert self._canvas is not None
        for x in range(layout.width):
            for y in range(layout.height):
                x0 = x * self.cell_size
                y0 = (layout.height - 1 - y) * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                pos = (x, y)
                if pos in layout.walls:
                    fill = "#1f4cff"
                else:
                    fill = "#000000"
                self._canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#222222")

                if pos in layout.foods:
                    pad = self.cell_size * 0.35
                    self._canvas.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill="#ffffff", outline="")
                if pos in layout.capsules:
                    pad = self.cell_size * 0.25
                    self._canvas.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill="#f5f5f5", outline="")

    def _draw_agent(self, pos: Position2D, color: str, tag: str) -> None:
        assert self._canvas is not None
        x, y = pos.x, pos.y
        x0 = x * self.cell_size
        y0 = (self._layout.height - 1 - y) * self.cell_size
        pad = self.cell_size * 0.12
        self._canvas.create_oval(x0 + pad, y0 + pad, x0 + self.cell_size - pad, y0 + self.cell_size - pad, fill=color, outline="", tags=tag)

    def render(self, game_stat: GameState) -> None:
        self._ensure_window(game_stat.layout)
        assert self._canvas is not None and self._root is not None

        self._canvas.delete("all")
        self._draw_static(game_stat.layout)

        self._canvas.delete("agent")
        self._draw_agent(game_stat.pacman_position, "#ffd84d", "agent")
        for idx, ghost_pos in enumerate(game_stat.ghost_positions):
            palette = ["#ff4d4d", "#4d8dff", "#ff9f43", "#45d6b0", "#d46bff"]
            self._draw_agent(ghost_pos, palette[idx % len(palette)], "agent")

        self._text_id = self._canvas.create_text(
            8,
            game_stat.layout.height * self.cell_size + 16,
            anchor="w",
            fill="white",
            font=("Arial", 12),
            text=f"Step: {game_stat.step_count}   Score: {game_stat.score:.1f}",
        )
        self._root.update_idletasks()
        self._root.update()

    def close(self) -> None:
        if self._root is not None:
            self._root.destroy()
        self._root = None
        self._canvas = None
        self._layout = None
