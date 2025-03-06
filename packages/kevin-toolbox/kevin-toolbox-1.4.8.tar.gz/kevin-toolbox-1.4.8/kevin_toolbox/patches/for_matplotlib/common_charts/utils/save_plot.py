import os


def save_plot(plt, output_path, dpi=200, suffix=".png", **kwargs):
    assert suffix in [".png", ".jpg", ".bmp"]

    if output_path is None:
        plt.show()
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=dpi)
