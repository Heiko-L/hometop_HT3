#!/bin/bash
#
 ##
 # #################################################################
 ## Copyright (c) 2023 Norbert S. <junky-zs at gmx dot de>
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
 # rev.: 0.2  date: 2023-03-17
 # rev.: 0.3  date: 2023-11-20 pip3 not used anymore.
 # rev.: 0.4  date: 2024-01-12 RPI.GPIO installation removed, 
 #                              see issues:#30 and #31
 #                             error-handling added.
 #################################################################
 #                                                               #
 # prepare os-parts and configuration for ht-project             #
 #                                                               #
 #################################################################

echo "=================================="
echo "update and upgrade os"
echo "----------------------------------"
sudo -v
if [ $? -ne 0 ]; then
 echo " -> sudo-call not allowed for this user, please ask the admin.";
 exit 1
fi

sudo apt-get update
sudo apt-get -y upgrade
echo "check and install required packages"
echo "----------------------------------"
echo "  >------- python3 --- --------<  "
which python3 >/dev/null
if [ $? -eq 0 ]; then
 echo " -> python3 available";
else
 echo "python3 NOT available -> installation started";
 sudo apt-get -y install python3;
fi
echo "----------------------------------"
echo "  >------- python3-serial -----<  "
sudo apt-get -y install python3-serial;
if [ $? -ne 0 ]; then
 echo "   !! 'python3-serial' installation failed !!"
 exit 1
fi
echo "----------------------------------"
echo "  >------- python3-setuptools -<  "
sudo apt-get -y install python3-setuptools;
if [ $? -ne 0 ]; then
 echo "   !! 'python3-setuptools' installation failed !!"
 exit 1
fi
echo "----------------------------------"
echo "  >------- python3-tk ---------<  "
sudo apt-get -y install python3-tk;
if [ $? -ne 0 ]; then
 echo "   !! 'python3-tk' installation failed !!"
 exit 1
fi
echo "----------------------------------"
echo "  >------- librrdtool-oo-perl--<  "
sudo apt-get -y install librrdtool-oo-perl;
if [ $? -ne 0 ]; then
 echo "   !! 'librrdtool-oo-perl' installation failed !!"
 exit 1
fi
echo "----------------------------------"
echo "  >------- rrdtool ------------<  "
sudo apt-get -y install rrdtool;
if [ $? -ne 0 ]; then
 echo "   !! 'rrdtool' installation failed !!"
 exit 1
fi
echo "----------------------------------"
currentuser=$(whoami)
echo "  >------- set user:${currentuser} dialout <  "
sudo adduser ${currentuser} dialout
echo "  >------- git ----------------<  "
which git >/dev/null
if [ $? -eq 0 ]; then
 echo " -> git available";
else
 echo "git NOT available -> installation started";
 sudo apt-get -y install git;
fi

machine=$(uname -m)
if expr "${machine}" : '^\(arm\|aarch\)' >/dev/null
  then
    # disable Bluetooth on RaspberryPi
    sudo systemctl disable hciuart >/dev/null
fi
echo "----- pre-setup done -------------"
