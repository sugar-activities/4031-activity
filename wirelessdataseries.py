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

import glob
import os

import gobject

from dataseries import DataSeries

sysfs_wireless_path_glob = "/sys/class/net/*/wireless/link"

def get_wireless_interfaces():
    return [path.split(os.path.sep)[4]
            for path in glob.glob(sysfs_wireless_path_glob)]

class WirelessDataSeries(DataSeries):
    def __init__(self, series_name=None, series_color=None, interface=None):
        DataSeries.__init__(self, series_name, series_color)
        if interface is None and len(get_wireless_interfaces()) > 0:
            interface = get_wireless_interfaces()[0]
        self.interface = interface
        self.sysfs_path = sysfs_wireless_path_glob.replace("*", self.interface)
        assert os.access(self.sysfs_path, os.R_OK), \
            "can't read from path %s" % self.sysfs_path
        self.timer = gobject.timeout_add(250, self.__timeout_cb)

    def __timeout_cb(self):
        self.record_new_value(self._get_next_value())
        return True

    def _get_next_value(self):
        reported = int(open(self.sysfs_path).read().strip())
        return reported / 100.0

