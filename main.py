#!/usr/bin/env python3
"""
Pacman 游戏入口。

用法示例:
    python main.py --layout engine/layouts/smallClassic.lay
"""

import argparse
import os
import sys

from engine.agent import PacmanKeyBoardAgent, BaseAgent
from engine.core import BasicGameRunner
from engine.layout import GameLayout
from engine.renderer import TKRenderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pacman Game")
    parser.add_argument(
        "--layout",
        type=str,
        default="engine/layouts/smallClassic.lay",
        help="地图文件路径 (默认: engine/layouts/smallClassic.lay)",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="keyboard",
        choices=["keyboard"],
        help="Pacman 智能体类型 (默认: keyboard)",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=32,
        help="每个格子的像素大小 (默认: 32)",
    )
    return parser.parse_args()


def create_pacman_agent(agent_type: str) -> BaseAgent:
    if agent_type == "keyboard":
        return PacmanKeyBoardAgent()
    raise ValueError(f"不支持的 agent 类型: {agent_type}")


def main() -> int:
    args = parse_args()

    if not os.path.exists(args.layout):
        print(f"错误：地图文件不存在: {args.layout}", file=sys.stderr)
        return 1

    layout = GameLayout.from_file(args.layout)
    pacman_agent = create_pacman_agent(args.agent)


    renderer = TKRenderer(cell_size=args.cell_size)

    runner = BasicGameRunner(layout, pacman_agent, renderer,)

    try:
        runner.run()
    except KeyboardInterrupt:
        print("\n 游戏被用户中断")
    finally:
        renderer.close()

    final_state = runner.get_game_state()
    if final_state.is_gameWin:
        print(f"胜利！最终得分: {final_state.score}, 步数: {final_state.step_count}")
    else:
        print(f"游戏结束，最终得分: {final_state.score}, 步数: {final_state.step_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
