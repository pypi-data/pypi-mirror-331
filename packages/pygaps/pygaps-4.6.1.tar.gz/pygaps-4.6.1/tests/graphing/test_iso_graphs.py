"""
Tests for the isotherm graphs
"""

import pytest

from pygaps.graphing.isotherm_graphs import plot_iso

from ..test_utils import mpl_cleanup


@pytest.mark.graphing
class TestIsothermGraphs():
    """Tests regular isotherm graphs"""
    @mpl_cleanup
    def test_basic_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm)

    @mpl_cleanup
    def test_multi_plot(self, basic_pointisotherm):
        plot_iso([
            basic_pointisotherm,
            basic_pointisotherm,
            basic_pointisotherm,
        ])

    @mpl_cleanup
    def test_data_plot(self, basic_pointisotherm):
        plot_iso(
            basic_pointisotherm,
            x_data='pressure',
            y1_data='loading',
            y2_data='enthalpy',
        )
        plot_iso(
            basic_pointisotherm,
            x_data='loading',
            y1_data='enthalpy',
        )

    @mpl_cleanup
    def test_branch_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, branch='ads')
        plot_iso(basic_pointisotherm, branch='des')
        plot_iso(basic_pointisotherm, branch='all')

    @mpl_cleanup
    def test_convert_plot(self, use_adsorbate, basic_pointisotherm):
        plot_iso(basic_pointisotherm, pressure_unit='Pa')
        plot_iso(basic_pointisotherm, loading_unit='mol')
        plot_iso(basic_pointisotherm, pressure_mode='relative')

    @mpl_cleanup
    def test_range_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, x_range=(0, 4))
        plot_iso(basic_pointisotherm, x_range=(0, None))
        plot_iso(basic_pointisotherm, y1_range=(3, None))
        plot_iso(basic_pointisotherm, y1_range=(3, None))
        plot_iso(basic_pointisotherm, y2_range=(3, 100))
        plot_iso(basic_pointisotherm, y2_range=(None, 10))

    @mpl_cleanup
    def test_log_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, logx=True)
        plot_iso(basic_pointisotherm, logy1=True)
        plot_iso(basic_pointisotherm, logy2=True)

    @mpl_cleanup
    def test_color_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, color=False)
        plot_iso(basic_pointisotherm, color=3)
        plot_iso(basic_pointisotherm, color=['red'])

    @mpl_cleanup
    def test_marker_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, marker=False)
        plot_iso(basic_pointisotherm, marker=3)
        plot_iso(basic_pointisotherm, marker=['o'])

    @mpl_cleanup
    def test_style_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, y1_line_style=dict(linewidth=5))

    @mpl_cleanup
    def test_legend_plot(self, basic_pointisotherm):
        plot_iso(basic_pointisotherm, lgd_keys=['material', 'temperature'])
