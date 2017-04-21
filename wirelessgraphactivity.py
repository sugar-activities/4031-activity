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

import logging

import gtk

from gettext import gettext as _
from sugar import profile
from sugar.activity import activity
from sugar.graphics import style
from sugar.graphics import xocolor
from sugar.graphics.icon import Icon

from wirelessgraph import Graph
from wirelessdataseries import WirelessDataSeries, get_wireless_interfaces

class WirelessGraphActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self._logger = logging.getLogger("WirelessGraph")
        self._logger.info("WirelessGraphActivity self.show()")

        self.set_title(_('WirelessGraph'))

        self._build_toolbox()
        self._build_mainbox()
        self._build_series()

    def _build_mainbox(self):
        self.vbox = gtk.VBox()

        if len(get_wireless_interfaces()) > 0:
            self.graph = Graph()
            self.vbox.pack_start(self.graph)
        else:
            icon = Icon(pixel_size=style.XLARGE_ICON_SIZE,
                        icon_name='icon-missing',
                        xo_color=xocolor.XoColor("%s,%s" % (
                        style.COLOR_BUTTON_GREY.get_svg(),
                        style.COLOR_TRANSPARENT.get_svg())))
            text = gtk.Label()
            text.set_markup('<span size="xx-large">'
                            'No wireless devices found</span>')
            text.set_line_wrap(True)
            text.set_alignment(0.5, 0)
            text.set_justify(gtk.JUSTIFY_CENTER)
            self.vbox.pack_start(icon)
            self.vbox.pack_start(text)
            self.vbox.show_all()

        self.set_canvas(self.vbox)
        self.vbox.show_all()

    def _build_series(self):
        self.series = []

        interfaces = get_wireless_interfaces()
        if len(interfaces) > 0:
            series = WirelessDataSeries(series_name=profile.get_nick_name(),
                                        series_color=profile.get_color(),
                                        interface=interfaces[0])
            self.series.append(series)
            self.graph.add_series(series)
            for interface in interfaces[1:]:
                series_name = "%s-%s" % (profile.get_nick_name(), interface)
                series_colors = xocolor.colors[hash(series_name)
                                               % len(xocolor.colors)]
                series_xocolor = xocolor.XoColor(",".join(series_colors))
                series = WirelessDataSeries(series_name=series_name,
                                            series_color=series_xocolor,
                                            interface=interface)
                self.series.append(series)
                self.graph.add_series(series)

    def _build_toolbox(self):
        toolbox = activity.ActivityToolbox(self)
        toolbox.show()
        self.set_toolbox(toolbox)
