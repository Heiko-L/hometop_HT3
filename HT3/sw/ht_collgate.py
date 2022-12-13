#! /usr/bin/python3
#
#################################################################
## Copyright (c) 2013 Norbert S. <junky-zs@gmx.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################
# Ver:0.1    / Datum 11.06.2017 first release
# Ver:0.2    / Datum 12.12.2022 update with wait-time before start.
#################################################################

import sys
sys.path.append('lib')
import Ccollgate
import time

__author__  = "junky-zs"
__status__  = "draft"
__version__ = "0.2"
__date__    = "12.12.2022"


cfg_pathfilename = './etc/config/collgate_cfg.xml'
collgate = Ccollgate.ccollgate(cfg_pathfilename)

# wait-time to be sure server (ht_proxy.py) is running
time.sleep(2.0)

collgate.start()
