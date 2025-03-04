import matplotlib.pyplot as plt
import numpy as np


def plot_function():
    x = np.linspace(-10, 10, 400)
    y = x**2

    plt.plot(x, y)
    plt.title("Graph of y = x^2")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.gca().spines["bottom"].set_color("yellow")
    plt.gca().spines["left"].set_color("yellow")
    plt.gca().spines["top"].set_color("yellow")
    plt.gca().spines["right"].set_color("yellow")
    plt.gca().xaxis.label.set_color("yellow")
    plt.gca().yaxis.label.set_color("yellow")
    plt.gca().tick_params(axis="x", colors="yellow")
    plt.gca().tick_params(axis="y", colors="yellow")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    plot_function()
