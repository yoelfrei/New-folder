import matplotlib.pyplot as plt


def main() -> None:
    x = [1, 2, 3, 4, 5, 6]
    y = [1, 4, 9, 16, 25, 36]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, y, marker="o", linewidth=2)
    plt.title("Example Graph: y = x^2")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig("example_plot.png", dpi=160)
    plt.show()


if __name__ == "__main__":
    main()
