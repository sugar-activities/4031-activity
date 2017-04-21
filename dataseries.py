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

import gobject

from sugar import profile
from sugar.graphics.style import Color
from sugar.graphics.xocolor import XoColor


grey  = (0.6, 0.6, 0.6, 1.0)


def _mean(data, previous_mean=None):
    return sum(data) / float(len(data))

def _central_moment(moment, mean, data, previous_moment=None):
    n = float(len(data))
    return pow((1 / n) * sum([pow((d - mean), moment) for d in data]), 1/moment)


class DataSeries(gobject.GObject):
    """encapsulates changable numeric data and their moments"""

    __gsignals__ = {
        'data-changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ([])),
        }

    def __init__(self, series_name=None, series_color=None):
        gobject.GObject.__init__(self)
        self.series_name = series_name \
            if series_name is not None else profile.get_nick_name()
        self.data_length = 40
        self.shrink_by = 1
        self.data_moments = (0, 1, 2, 3)
        self.data = []
        self.moments = [[] for m in self.data_moments]
        self.set_color(series_color if series_color is not None else XoColor())

    def set_color(self, xo_color):
        self.colors = (Color(xo_color.stroke).get_rgba(),
                       Color(xo_color.fill).get_rgba(),
                       grey)

    def record_new_value(self, new_value):
        """record a new value for a nick_name (default: for self.nick_name)"""
        self.data.append(new_value)

        if len(self.data) > self.data_length:
            del self.data[:self.shrink_by]

        for moment in self.data_moments[1:]:
            means = self.moments[1]
            moments = self.moments[moment]

            if moment == 1:
                moments.append(_mean(self.data))
            else:
                moments.append(_central_moment(moment, means[-1], self.data))

            if len(moments) > self.data_length:
                del moments[:self.shrink_by]

        self.emit('data-changed')

