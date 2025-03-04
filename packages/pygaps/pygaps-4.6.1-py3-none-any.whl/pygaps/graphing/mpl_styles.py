"""Contains global style dictionaries for matplotlib to be applied."""

import typing as t

#: Markers used in plotting.
ISO_MARKERS: "tuple[str]" = ('o', 's', 'D', 'P', '*', '<', '>', 'X', 'v', '^')
#: Colors used in main (y1) plotting.
Y1_COLORS: "tuple[str]" = ('#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600')
#: Colors used in secondary (y2) plotting.
Y2_COLORS: "tuple[str]" = ("#0082bd", "#8674c5", "#d15d9e", "#ea5e59", "#ca8300")

#: Style applied to ALL matplotlib figures in pygaps.
BASE_STYLE: "dict[str, t.Any]" = {
    'legend.frameon': False,
}

#: Style applied to Isotherm figures.
ISO_STYLE: "dict[str, t.Any]" = {
    'figure.figsize': (6, 6),
    'axes.titlesize': 20,
    'axes.titley': 1.01,
    'axes.labelsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'legend.handlelength': 2,
    'legend.fontsize': 11,
    'image.aspect': 'equal'
}

#: Style component to generate "muted/unselected" points.
POINTS_MUTED: "dict[str, t.Any]" = {
    "lines.linestyle": 'none',
    "lines.marker": 'o',
    "lines.markerfacecolor": 'none',
    "lines.markeredgecolor": 'grey',
    "lines.markersize": 5,
    "lines.markeredgewidth": 1.5,
}

#: Style component to generate "highlighted/elected" points.
POINTS_HIGHLIGHTED: "dict[str, t.Any]" = {
    "lines.linestyle": 'none',
    "lines.marker": 'o',
    "lines.markeredgecolor": 'r',
    "lines.markerfacecolor": 'r',
    "lines.markersize": 5,
}

#: Style component to generate "single important" points.
POINTS_IMPORTANT: "dict[str, t.Any]" = {
    "lines.linestyle": 'none',
    "lines.marker": 'X',
    "lines.markeredgecolor": 'k',
    "lines.markerfacecolor": 'k',
    "lines.markersize": 10,
}

#: Style component to generate a line fitted through points.
LINE_FIT: "dict[str, t.Any]" = {
    "lines.linestyle": '--',
    "lines.marker": '',
}

#: Style component to apply to error bars.
LINE_ERROR: "dict[str, t.Any]" = {
    "lines.linestyle": '--',
    "lines.marker": 'o',
    "lines.markersize": 3,
}
