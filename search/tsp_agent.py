import math
import networkx as nx


from engine.agent import BaseAgent
from engine.core import GameState
from engine.layout import Layout

class PacmanTSPSearchAgent(BaseAgent):
    
    def __init__(self, layout: Layout):
        super().__init__()
        self.G = nx.Graph()
        self.cached_path = {}
    
    def _build_graph(self, layout: Layout):
        # 为可行走的区域构建一个树, 从左上角到右下角构建, 避免重复
        G = nx.Graph()
        wall = layout.walls
        
        for y in range(layout.height):
            for x in range(layout.width):
                pos = (x, y)
                if pos in wall:
                    continue
                G.add_node(pos)
                # 连接右、下邻居
                for dx, dy in [(0, 1), (1, 0)]:
                    nx, ny = x + dx, y + dy
                    if nx < layout.width and ny < layout.height and (nx, ny) not in wall:
                        G.add_edge(pos, (nx, ny), weight=1)
        
        self._simplify_graph(G, layout)
        self.G = G
    
    def _simplify_graph(self, G: nx.Graph, layout: Layout):
        # 简化图
        # 重复以下简化的策略直到无法再执行:
        # 1. 删除度为 2 的非 food 点，改成直接连接
        # 2. 删除度为 1 的非 food 点（树的末端, 不需要走）
        foods = set(layout.foods)
        changed = True

        while changed:
            changed = False
            for node in list(G.nodes):
                if node in foods:
                    continue
            
                degree = G.degree[node]

                if degree == 1:
                    G.remove_node(node)
                    changed = True

                if degree == 2:
                    neighbors = list(G.neighbors(node))
                    u, v = neighbors

                    weight_via_uv = G[u][node]['weight'] + G[node][v]['weight']
                    # 如果通过 u-v 的权重更小，则删除节点并连接 u-v
                    if G.has_edge(u, v):
                        G[u][v]['weight'] = min(G[u][v]['weight'], weight_via_uv)
                    else:
                        G.add_edge(u, v, weight=weight_via_uv)
                    
                    G.remove_node(node)
                    changed = True