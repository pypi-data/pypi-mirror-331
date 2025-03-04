from re import search

import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure as Fig


from .utils import dict_unit_en


try: plt.switch_backend('TkAgg')
except: pass

# try: plt.rcParams['font.family'] ='Malgun Gothic'
# except: pass

mplstyle.use('fast')


def convert_unit(value: float, digit=0, word='usd'):
    v = value.__abs__()
    du = dict_unit_en
    for unit, n in du.items():
        if n <= v:
            num = (value / n).__round__(digit)
            if not num % 1: num = int(num)
            return f'{num:,}{unit} {word}'
    value = value.__round__(digit)
    if not value % 1: value = int(value)
    elif value < 10: digit = 2
    text = f'{value:,}{word}'
    return text


class Figure(Fig):
    canvas: FigureCanvasAgg


class Base:
    figure: Figure

    figsize = (14, 7)
    ratio_ax_legend, ratio_ax_price, ratio_ax_volume = (2, 18, 5)
    adjust = dict(
        top=0.95, bottom=0.05, left=0.01, right=0.93,
        wspace=0, hspace=0
    )

    title = 'seolpyo mplchart'
    color_background = '#fafafa'
    gridKwargs = {}
    color_tick, color_tick_label = ('k', 'k')

    unit_price, unit_volume = ('usdt', 'usdt')

    def draw_canvas(self): return self.figure.canvas.draw()
    def blit_canvas(self): return self.figure.canvas.blit()

    def __init__(self, *args, **kwargs):
        plt.rcParams['toolbar'] = 'None'
        # plt.rcParams['figure.dpi'] = 600

        self._get_plot()
        return

    def _get_plot(self):
        self.figure, axes = plt.subplots(
            3, # row
            figsize=self.figsize,
            height_ratios=(self.ratio_ax_legend, self.ratio_ax_price, self.ratio_ax_volume) # row
        )
        axes: list[Axes]
        self.ax_legend, self.ax_price, self.ax_volume = axes
        self.ax_legend.set_label('legend ax')
        self.ax_price.set_label('price ax')
        self.ax_volume.set_label('volume ax')

        self.figure.canvas.manager.set_window_title(f'{self.title}')
        self.figure.set_facecolor(self.color_background)

        # (Configure subplots)
        self.figure.subplots_adjust(**self.adjust)

        self.ax_legend.set_axis_off()

        # y ticklabel foramt
        self.ax_price.yaxis.set_major_formatter(lambda x, _: convert_unit(x, word=self.unit_price, digit=2))
        self.ax_volume.yaxis.set_major_formatter(lambda x, _: convert_unit(x, word=self.unit_volume, digit=2))

        gridKwargs = {'visible': True, 'linewidth': 0.7, 'color': '#d0d0d0', 'linestyle': '-', 'dashes': (1, 0)}
        gridKwargs.update(self.gridKwargs)
        for ax in (self.ax_price, self.ax_volume):
            ax.xaxis.set_animated(True)
            ax.yaxis.set_animated(True)

            # x tick
            ax.xaxis.set_ticks_position('none')
            # x tick label
            ax.set_xticklabels([])
            # y tick
            ax.tick_params(left=False, right=True, labelleft=False, labelright=True, colors=self.color_tick_label)
            # Axes
            for i in ['top', 'bottom', 'left', 'right']: ax.spines[i].set_color(self.color_tick)

            ax.set_facecolor(self.color_background)

            ax.grid(**gridKwargs)
        return

