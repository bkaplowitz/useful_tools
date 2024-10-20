import matplotlib as mpl
import plotnine as pn


def mpl_theme(width=12, height=8):
    return [
        pn.theme_matplotlib(),
        pn.theme(
            figure_size=(width, height),
            strip_background=pn.element_rect(color="w", fill="w"),
            panel_grid=pn.element_line(color="k", alpha=0.1),
        ),
    ]


def poster_sizes():
    return pn.theme(
        text=pn.element_text(size=18),
        title=pn.element_text(size=18),
        legend_title=pn.element_text(size=18),
    )


class IEEE(pn.theme):
    def __init__(self, figsize=(3.487, 2.155)):
        # https://matplotlib.org/stable/tutorials/introductory/customizing.html
        margin = {"t": 1, "b": 1, "l": 1, "r": 1, "units": "pt"}
        super().__init__(
            axis_title_x=pn.element_text(margin=margin),
            axis_title_y=pn.element_text(margin=margin),
            strip_background_x=pn.element_text(color="w", height=0.1),
            strip_background_y=pn.element_text(color="w", width=0.1),
            legend_key_width=10,
            legend_key_height=10.0,
            legend_text_colorbar=pn.element_text(size=6.0),
            complete=True,
        )

        self._rcParams.update({
            "figure.figsize": figsize,
            "figure.dpi": 300,
            "font.family": "serif",
            "font.size": 6,
            "axes.grid": True,
            "axes.grid.which": "both",
            "grid.linewidth": 0.25,
            "grid.alpha": 0.2,
            "axes.linewidth": 0.5,
            "axes.prop_cycle": mpl.rcParams["axes.prop_cycle"],
        })


def no_colorbar_ticks():
    return pn.guides(color=pn.guide_colorbar(ticks=False))


def sig_figs(x, n=1):
    return "{:g}".format(float("{:.{p}g}".format(x, p=n)))
