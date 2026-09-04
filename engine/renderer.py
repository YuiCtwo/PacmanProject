from __future__ import annotations

import math
import sys
import tkinter as tk

from typing import Callable, Iterable, List, Optional, Protocol, Sequence, Tuple, Set

from engine.core import Action, GameState
from engine.layout import GameLayout
from utils.pos_utils import Position2D

from engine.constant import INFO_PANE_HEIGHT


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t

def interpolate_position(start: Position2D, end: Position2D, t: float) -> Position2D:
    return Position2D(
        lerp(start.x, end.x, t),
        lerp(start.y, end.y, t)
    )

class GameRenderer(Protocol):
    def render(self, game_stat: GameState) -> None: ...
    def close(self) -> None: ...

class NullRenderer:
    def render(self, game_stat) -> None:
        pass
    def close(self) -> None:
        pass


class TKRenderer:
    def __init__(self, cell_size: int = 32, title: str = "Pacman", num_frame: int = 4, frame_time: float = 0.1):
        self.cell_size = cell_size
        self._title = title
        
        self._root = None
        self._canvas = None
        self._text_id = None
        self._text_formatter = "Step: %d   Score: %d"
        self._layout = None
        self._tk = None
        self._keys: Set[str] = set()
        
        self._frame_time = frame_time
        
        self._pacman_item = None
        self._ghost_items: List[List[int]] = []
        self._ghost_base_colors: List[str] = []
        self._key_press_callbacks: List[Callable[[str], None]] = []
        self._key_release_callbacks: List[Callable[[str], None]] = []

    def _bind_events(self) -> None:
        self._root.bind("<KeyPress>", self._on_key_press)
        self._root.bind("<KeyRelease>", self._on_key_release)
        self._canvas.focus_set()

    def register_key_press_callback(self, callback: Callable[[str], None]) -> None:
        """注册按键按下事件回调，供 PacmanKeyBoardAgent 使用。"""
        self._key_press_callbacks.append(callback)

    def register_key_release_callback(self, callback: Callable[[str], None]) -> None:
        """注册按键释放事件回调，供 PacmanKeyBoardAgent 使用。"""
        self._key_release_callbacks.append(callback)

    def _on_key_press(self, event: tk.Event) -> None:
        """全局按键按下处理。"""
        if event.keysym in ("w", "a", "s", "d", "q"):
            self._keys.add(event.keysym)
        for callback in self._key_press_callbacks:
            callback(event.keysym)

    def _on_key_release(self, event: tk.Event) -> None:
        """全局按键释放处理。"""
        if event.keysym in ("w", "a", "s", "d", "q"):
            self._keys.discard(event.keysym)
        for callback in self._key_release_callbacks:
            callback(event.keysym)

    def _ensure_window(self, game_stat: GameState) -> None:
        layout = game_stat.layout
        if self._root is None:
            self._tk = tk
            self._root = tk.Tk()
            self._root.title(self._title)
            self._canvas = tk.Canvas(self._root, bg="black", highlightthickness=0)
            self._canvas.pack()
            self._bind_events()

        if self._layout != layout:
            self._canvas.delete("all")
            self._text_id = None
            self._pacman_item = None
            self._ghost_items = []
            self._layout = layout
            width = layout.width * self.cell_size
            height = layout.height * self.cell_size + INFO_PANE_HEIGHT
            self._canvas.config(width=width, height=height)
            self._root.geometry(f"{width}x{height}")

            self._draw_map(game_stat.layout)
            self._draw_food(game_stat)
            self._draw_capsule(game_stat)
            self._draw_text(game_stat.layout)
            self._draw_pacman(game_stat.layout)
            self._draw_ghosts(game_stat.layout)

    def _draw_map(self, layout: GameLayout) -> None:
        """绘制地图背景与墙体。"""
        for x in range(layout.width):
            for y in range(layout.height):
                x0 = x * self.cell_size
                y0 = (layout.height - 1 - y) * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                pos = (x, y)
                fill = "#1f4cff" if pos in layout.walls else "#000000"
                self._canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#222222", tags="static")

    def _draw_food(self, game_stat: GameState) -> None:
        """绘制普通豆子。"""
        layout = game_stat.layout
        pad = self.cell_size * 0.35
        for (x, y), visible in game_stat.food_visible.items():
            if not visible:
                continue
            x0 = x * self.cell_size
            y0 = (layout.height - 1 - y) * self.cell_size
            x1 = x0 + self.cell_size
            y1 = y0 + self.cell_size
            self._canvas.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill="#ffffff", outline="", tags="food")

    def _draw_capsule(self, game_stat: GameState) -> None:
        """绘制大力丸。"""
        layout = game_stat.layout
        pad = self.cell_size * 0.25
        for (x, y), visible in game_stat.capsule_visible.items():
            if not visible:
                continue
            x0 = x * self.cell_size
            y0 = (layout.height - 1 - y) * self.cell_size
            x1 = x0 + self.cell_size
            y1 = y0 + self.cell_size
            self._canvas.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill="#f5f5f5", outline="", tags="capsule")

    def _get_cell_pos(self, pos: Position2D) -> Tuple[float, float]:
        x = (pos.x + 0.5) * self.cell_size
        y = (self._layout.height - 1 - pos.y + 0.5) * self.cell_size
        return x, y

    def _compute_pacman_animation(self, pos: Position2D, direction: Action):
        """Pacman 动画"""
        px = self._get_cell_pos(pos)
        cx, cy = px
        r = 0.5 * self.cell_size
        bbox = (cx - r, cy - r, cx + r, cy + r)

        t = pos.x - int(pos.x) + pos.y - int(pos.y)
        width = 30 + 80 * math.sin(math.pi * t)
        delta = width / 2
        if direction == Action.LEFT:
            start, end = 180 + delta, 180 - delta
        elif direction == Action.UP:
            start, end = 90 + delta, 90 - delta
        elif direction == Action.DOWN:
            start, end = 270 + delta, 270 - delta
        else:  # RIGHT or STOP
            start, end = 0 + delta, 0 - delta
        return bbox, start, end - start
    
    def get_pacman_chara(self, pos: Position2D, direction: Action) -> int:
        """创建 Pacman"""
        bbox, start, extend = self._compute_pacman_animation(pos, direction)
        return self._canvas.create_arc(
            *bbox, start=start, extent=extend,
            fill="#ffff3d", outline="#ffff3d", width=2,
            style=tk.PIESLICE, tags="agent"
        )

    def _draw_pacman(self, layout: GameLayout) -> None:
        """绘制 Pacman"""
        self._pacman_item = self.get_pacman_chara(layout.pacman_start, Action.STOP)

    def _compute_ghost_animation(self, pos: Position2D) -> Tuple[List[float], Tuple[Tuple[float, float, float, float], ...]]:
        """Ghost 动画 (body_points, eye_bboxes)"""
        px = self._get_cell_pos(pos)
        cx, cy = px
        scale = self.cell_size * 0.65 / 2
        shape = [
            (-1.0, 0.6), (-1.0, -0.3), (-0.6, -1.0), (0.6, -1.0),
            (1.0, -0.3), (1.0, 0.6), (0.7, 0.3), (0.4, 0.6),
            (0.1, 0.3), (-0.2, 0.6), (-0.5, 0.3)
        ]
        body_points = [coord for sx, sy in shape for coord in (cx + sx * scale, cy + sy * scale)]

        eye_r = scale * 0.22
        pupil_r = scale * 0.10
        left_center = (cx - scale * 0.35, cy - scale * 0.35)
        right_center = (cx + scale * 0.35, cy - scale * 0.35)
        left_eye = (left_center[0] - eye_r, left_center[1] - eye_r, left_center[0] + eye_r, left_center[1] + eye_r)
        right_eye = (right_center[0] - eye_r, right_center[1] - eye_r, right_center[0] + eye_r, right_center[1] + eye_r)
        left_pupil = (left_center[0] - pupil_r, left_center[1] - pupil_r, left_center[0] + pupil_r, left_center[1] + pupil_r)
        right_pupil = (right_center[0] - pupil_r, right_center[1] - pupil_r, right_center[0] + pupil_r, right_center[1] + pupil_r)
        eye_bboxes = (left_eye, right_eye, left_pupil, right_pupil)

        return body_points, eye_bboxes

    def get_ghost_chara(self, pos: Position2D, color: str, ghost_id: int) -> List[int]:
        """创建 Ghost（身体 + 双眼 + 双瞳孔）"""
        body_points, eye_bboxes = self._compute_ghost_animation(pos)
        tag = f"ghost_{ghost_id}"
        body = self._canvas.create_polygon(body_points, fill=color, outline=color, tags=tag)
        parts = [body]
        for idx, bbox in enumerate(eye_bboxes):
            fill = "#ffffff" if idx < 2 else "#000000"
            parts.append(self._canvas.create_oval(*bbox, fill=fill, outline="", tags=tag))
        return parts

    def _draw_ghosts(self, layout: GameLayout) -> None:
        """绘制 Ghost"""
        palette = ["#ff4d4d", "#4d8dff", "#ff9f43", "#45d6b0", "#d46bff"]
        self._ghost_items = []
        self._ghost_base_colors = []
        for idx, pos in enumerate(layout.ghost_starts):
            color = palette[idx % len(palette)]
            self._ghost_base_colors.append(color)
            self._ghost_items.append(self.get_ghost_chara(pos, color, idx))

    def _draw_text(self, layout: GameLayout):
        self._text_id = self._canvas.create_text(8, layout.height * self.cell_size + 16,
            anchor="w", fill="white", font=("Arial", 12),
            text=self._text_formatter % (0, 0),
        )

    def _sleep(self, secs: float) -> None:
        """sleep：在等待期间运行事件循环，保持 UI 响应。"""
        self._root.update_idletasks()
        self._root.after(int(1000 * secs), self._root.quit)
        self._root.mainloop()

    def render(self, game_stat: GameState) -> None:
        self._ensure_window(game_stat)

        for i in range(1, self.num_frame + 1):
            dt = i / self.num_frame

            # Pacman 插值移动 + 更新嘴巴角度
            pacman_pos = interpolate_position(game_stat.pacman_prev_pos, game_stat.pacman_position, dt)
            bbox, start, extent = self._compute_pacman_animation(pacman_pos, game_stat.pacman_action)
            self._canvas.coords(self._pacman_item, *bbox)
            self._canvas.itemconfig(self._pacman_item, start=start, extent=extent)
           
            # Ghost 插值移动 + Scared 状态颜色
            for idx, ghost_item in enumerate(self._ghost_items):
                ghost_prev_pos = game_stat.ghost_prev_pos[idx]
                ghost_end_pos = game_stat.ghost_positions[idx]
                ghost_pos = interpolate_position(ghost_prev_pos, ghost_end_pos, dt)
                body_points, eye_bboxes = self._compute_ghost_animation(ghost_pos)
                self._canvas.coords(self._ghost_items[idx][0], body_points)
                for item, bbox in zip(self._ghost_items[idx][1:], eye_bboxes):
                    self._canvas.coords(item, *bbox)

                # 根据 scared 时间更新身体与眼睛颜色
                scared_time = game_stat.ghost_scared_time[idx]
                base_color = self._ghost_base_colors[idx]
                if scared_time > 0:
                    # 剩余时间不多时闪烁预警
                    if scared_time <= 5 and (game_stat.step_count % 2 == 0):
                        body_color = base_color
                    else:
                        body_color = "#c0c0ff"
                    # 眼球保持白色，瞳孔与身体同色形成"惊恐大眼"
                    eye_colors = ["#ffffff", "#ffffff", body_color, body_color]
                else:
                    body_color = base_color
                    eye_colors = ["#ffffff", "#ffffff", "#000000", "#000000"]

                self._canvas.itemconfig(
                    self._ghost_items[idx][0], fill=body_color, outline=body_color
                )
                for item, color in zip(self._ghost_items[idx][1:], eye_colors):
                    self._canvas.itemconfig(item, fill=color)

            self._canvas.update_idletasks()
            self._canvas.update()
            self._sleep(self._frame_time / self.num_frame)

        # 隐藏吃掉的豆和大力丸：直接删除整层后按当前状态重绘
        self._canvas.delete("food")
        self._draw_food(game_stat)
        self._canvas.delete("capsule")
        self._draw_capsule(game_stat)

        self._canvas.itemconfig(self._text_id, text=self._text_formatter % (game_stat.step_count, game_stat.score))

        self._root.update_idletasks()
        self._root.update()

    @property
    def get_keys(self) -> Set[str]:
        return set(self._keys)


    def close(self) -> None:
        if self._root is not None:
            self._root.destroy()
        self._root = None
        self._canvas = None
        self._layout = None
