# Copyright (C) 2009, Martin Dengler <martin@martindengler.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import cairo
import gtk
import gtk.gdk


black = (0.0, 0.0, 0.0, 1.0)
blue  = (0.2, 0.0, 0.8, 1.0)
red   = (1.0, 0.0, 0.0, 1.0)


class Graph(gtk.Image):
    """Displays a graph of changing linear data points

    TODO: improve this overview
    """
    def __init__(self, *args, **kwargs):
        gtk.Image.__init__(self, *args, **kwargs)
        self.connect_after("expose-event", self.__expose_event_cb)
        self.line_width = 0.05
        self.width = 1.0
        self.padding_x = 0.05
        self.series = []
        self.signals = {}

    def add_series(self, series):
        self.signals[series] = series.connect('data-changed',
                                              self.__data_changed_cb)
        self.series.append(series)

    def remove_series(self, series):
        series.disconnect(self.signals[series])
        del self.signals[series]
        self.series.remove(series)

    def __data_changed_cb(self, *args, **kwargs):
        x, y, w, h = self.allocation
        self.window.invalidate_rect((x, y, x+w, y+h), False)

    def __expose_event_cb(self, widget, event):
        """sets up a unit-height canvas for the drawing method"""
        cr = self._get_cairo_region()
        self._draw_frame(cr)
        if len(self.series[0].data) > 0:
            self._draw_lines(cr)
            self._draw_metrics(cr)

    def _get_cairo_region(self):
        cr = self.window.cairo_create()
        x, y, w, h = self.allocation
        cr.translate(x, y)
        cr.scale(float(h), float(h))
        self.width = w / float(h)
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        return cr

    def _draw_frame(self, cr):
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.move_to(0, 0)
        cr.line_to(self.width, 0)
        cr.line_to(self.width, 1.0)
        cr.line_to(0, 1.0)
        cr.line_to(0, 0)
        cr.stroke()

    def _draw_lines(self, cr):
        tick_line_width = 0.005

        for series in self.series:
            data = series.data
            means = series.moments[1]
            colors = series.colors
            self._plot_line(cr, colors[0], self.line_width, data)
            self._plot_line(cr, colors[1], tick_line_width, means)

            line1_tick_offset = -(self.padding_x / 1.99)
            self._tick_mark(cr,
                            colors[0],
                            self.padding_x / 2.0,
                            self.line_width, data[-1],
                            tick_x_offset=line1_tick_offset)
            self._tick_mark(cr,
                            colors[1],
                            self.padding_x,
                            tick_line_width,
                            means[-1],
                            label="%i" % (means[-1] * 100))

            min_datum = min(data)
            max_datum = max(data)
            self._tick_mark(cr,
                            colors[2],
                            self.padding_x,
                            tick_line_width,
                            min_datum,
                            tick_x_offset=line1_tick_offset,
                            label="%i" % (min_datum * 100))
            self._tick_mark(cr,
                            colors[2],
                            self.padding_x,
                            tick_line_width,
                            max_datum,
                            tick_x_offset=line1_tick_offset,
                            label="%i" % (max_datum * 100))


    def _draw_metrics(self, cr):
        cr.set_font_size(0.09)
        if len(self.series) > 0:
            series = self.series[0]
            colors = series.colors
            data = series.data
            means = series.moments[1]

            self._draw_outlined_text(cr,
                                     "Link quality: %i" % (data[-1] * 100),
                                     colors[0],
                                     (0.0, 0.9))

            self._draw_outlined_text(cr,
                                     "Mean: %i" % (means[-1] * 100),
                                     colors[1],
                                     (0.79, 0.9))

    def _plot_line(self, cr, color, line_width, data, offset=0.0):
        dx = (self.width - (2 * self.padding_x)) / float(len(data))
        last_x = 0.0
        last_y = 1.0 - data[0] - offset

        cr.set_line_width(line_width)
        cr.set_source_rgba(*color)
        cr.move_to(last_x, last_y)
        for idx in range(1, len(data[1:])):
            cur_y = 1.0 - data[idx] - offset
            dy = cur_y - last_y
            cr.rel_line_to(dx, dy)
            last_x += dx
            last_y += dy
        cr.stroke()

    def _tick_mark(self, cr, color, tick_width, line_width, datum,
                   tick_x_offset=0.0, label=None):
        cr.set_source_rgba(*color)
        cr.set_line_width(line_width)
        tick_y = 1.0 - datum
        tick_x = self.width - (2.0 * self.padding_x) + tick_x_offset
        cr.move_to(tick_x, tick_y)
        cr.line_to(tick_x + tick_width, tick_y)
        if label is not None:
            cr.set_font_size(0.035)
            cr.move_to(tick_x + tick_width, tick_y + line_width)
            cr.show_text(label)
        cr.stroke()

    def _draw_outlined_text(self, cr, text, color, pos, font_size=0.09):
        x, y = pos
        cr.set_source_rgba(*black)
        cr.move_to(x - (0.005 * x), y + (0.005 * y))
        cr.set_font_size(font_size * 1.005)
        cr.show_text(text)

        cr.set_source_rgba(*color)
        cr.move_to(x, y)
        cr.set_font_size(font_size)
        cr.show_text(text)



if __name__ == "__main__":
    graph = Graph()
    import wirelessdataseries
    graph.add_series(wirelessdataseries.WirelessDataSeries())

    vbox = gtk.VBox()
    vbox.pack_start(graph)

    w = gtk.Window()
    w.add(vbox)
    w.show_all()

    gtk.main()
