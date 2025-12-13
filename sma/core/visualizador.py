from typing import List
import matplotlib.pyplot as plt


class Visualizador2D:
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.set_window_title("SMA")

    def render(self, ambiente, agentes: List):
        if not hasattr(ambiente, "matriz"):
            return
        
        self.ax.clear()
        self.ax.imshow(ambiente.matriz, cmap="gray_r", origin="upper")

        for a in agentes:
            carregando = getattr(a, "carregando", 0)
            if carregando > 0:
                self.ax.scatter([a.posicao[0]], [a.posicao[1]], c="orange", marker="o", s=150,
                                edgecolors="red", linewidths=2, zorder=5)
                self.ax.text(a.posicao[0], a.posicao[1] - 0.3, f"{carregando}", ha='center', va='top',
                             color='white', fontweight='bold',
                             bbox=dict(boxstyle='round', facecolor='red', alpha=0.7), fontsize=8, zorder=6)
            else:
                self.ax.scatter([a.posicao[0]], [a.posicao[1]], c="red", marker="o", s=100, zorder=5)

        if hasattr(ambiente, "obstaculos") and ambiente.obstaculos:
            for ox, oy in ambiente.obstaculos:
                self.ax.scatter([ox], [oy], c="black", marker="s", s=300, zorder=2, edgecolors="darkgray", linewidths=1)

        if hasattr(ambiente, "pos_farol"):
            x, y = ambiente.pos_farol
            self.ax.scatter([x], [y], c="yellow", marker="*", s=200, zorder=4)
        
        if hasattr(ambiente, "ninho"):
            x, y = ambiente.ninho
            self.ax.scatter([x], [y], c="blue", marker="s", s=200, zorder=4)
        
        if hasattr(ambiente, "recursos"):
            for (rx, ry), val in ambiente.recursos.items():
                self.ax.scatter([rx], [ry], c="green", marker="D", s=150, zorder=3)
                self.ax.text(rx, ry + 0.3, f"{val}", ha='center', va='bottom', color='white', fontweight='bold',
                             bbox=dict(boxstyle='round', facecolor='green', alpha=0.7), fontsize=8, zorder=4)

        self.ax.set_xlim(-0.5, ambiente.largura - 0.5)
        self.ax.set_ylim(-0.5, ambiente.altura - 0.5)
        plt.pause(0.1)
        self.fig.canvas.draw()

    def finalizar(self):
        plt.ioff()
        plt.show(block=True)
