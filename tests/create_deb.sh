#!/bin/bash

SRC_DIR='/home/pablo/src/guifinetstudio'
DST_DIR='guifinetstudiodeb'
A_PYSHARED='calc.py champlainguifinet.py configmanager.py ui.py unsolclic.py utils.py'
A_DOC='README AUTHORS COPYING'
LIBCNML='__init__.py libcnml.py'
GUIFIAPI='__init__.py api.py constants.py error.py'
LOCALES='ca es eu gl'

alias cp='cp -v'

rm -vfr $DST_DIR
mkdir -p $DST_DIR/DEBIAN
mkdir -p $DST_DIR/usr/share/pyshared/guifinet-studio
mkdir -p $DST_DIR/usr/bin
mkdir -p $DST_DIR/usr/share/guifinet-studio
mkdir -p $DST_DIR/usr/share/applications
mkdir -p $DST_DIR/usr/share/doc/guifinet-studio
mkdir -p $DST_DIR/usr/lib/python2.7/dist-packages/libcnml
mkdir -p $DST_DIR/usr/lib/python2.7/dist-packages/pyGuifiAPI
mkdir -p $DST_DIR/usr/share/locale/


cat > $DST_DIR/DEBIAN/changelog << "EOF"
guifinet-studio (0.7-1) unstable; urgency=low

  * Initial release

 -- Pablo Castellano <pablo@anche.no>  Sat, 22 Sep 2012 14:41:21 +0200
EOF

echo '8' > $DST_DIR/DEBIAN/compat

cat > $DST_DIR/DEBIAN/control << "EOF"
Source: guifinet-studio
Section: net
Priority: extra
Maintainer: Pablo Castellano <pablo@anche.no>
Build-Depends: debhelper (>= 8.0.0)
Standards-Version: 3.9.2
Homepage: http://en.wiki.guifi.net/wiki/Guifi.net_Studio
Package: guifinet-studio
Version: 0.7
Architecture: all
Depends: python2.7, gir1.2-gtkchamplain-0.12, python-lxml, python-jinja2
Description: Guifi.net Studio (TEST PACKAGE)
 Guifi.net Studio aims to be the swiss army knife of wireless communities
 .
 It's focused on Guifi.net, the biggest wireless and cable community in
 the world.
 .
 You can visualize CNML data files.
 .
 NOTE: THIS IS A TEST PACKAGE. IT WAS BUILT MANUALLY AND IT CAN BE BUGGY
EOF

cat > $DST_DIR/DEBIAN/copyright << "EOF"
Format: http://dep.debian.net/deps/dep5
Upstream-Name: guifinet-studio
Source: <url://example.com>

Files: *
Copyright: <years> <put author's name and email here>
           <years> <likewise for another author>
License: GPL-3.0+

Files: debian/*
Copyright: 2012 Pablo Castellano <pablo@anche.no>
License: GPL-3.0+

License: GPL-3.0+
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".

# Please also look if there are files or directories which have a
# different copyright/license attached and list them here.
EOF

# DEBIAN/docs
# DEBIAN/files
# DEBIAN/rules

for f in $A_PYSHARED
do
	cp $SRC_DIR/$f $DST_DIR/usr/share/pyshared/guifinet-studio/
done

cp $SRC_DIR/guifinet_studio.py $DST_DIR/usr/bin/guifinet-studio
cp -r $SRC_DIR/ui $DST_DIR/usr/share/guifinet-studio/
cp $SRC_DIR/guifinet_studio_menu.ui $DST_DIR/usr/share/guifinet-studio/
cp $SRC_DIR/guifinet-studio.desktop $DST_DIR/usr/share/applications/

for f in $A_DOC
do
	cp $SRC_DIR/$f $DST_DIR/usr/share/doc/guifinet-studio/
done

for f in $LIBCNML
do
	cp $SRC_DIR/lib/libcnml/$f $DST_DIR/usr/lib/python2.7/dist-packages/libcnml/
done

for f in $GUIFIAPI
do
	cp $SRC_DIR/lib/pyGuifiAPI/$f $DST_DIR/usr/lib/python2.7/dist-packages/pyGuifiAPI/
done

# Otros cambios:
# champlainguifinet.py: quitar os.chdir y sys.path.append
# guifinet_studio.py: cambiar os.chdir y sys.path.append
grep -v "sys.path.append('lib')" $SRC_DIR/champlainguifinet.py | grep -v "os.chdir(os.path.dirname(os.path.abspath(__file__)))" > $DST_DIR/usr/share/pyshared/guifinet-studio/champlainguifinet.py
sed "s|os.chdir(os.path.dirname(os.path.abspath(__file__)))|os.chdir('/usr/share/guifinet-studio')|" $SRC_DIR/guifinet_studio.py  | sed "s|sys.path.append('lib')|sys.path.append('/usr/share/pyshared/guifinet-studio')|" | sed 's|with open("AUTHORS") as f:|with open("/usr/share/doc/guifinet-studio/AUTHORS") as f:|' | sed 's|with open("COPYING") as f:|with open("/usr/share/doc/guifinet-studio/COPYING") as f:|' > $DST_DIR/usr/bin/guifinet-studio
sed "s|I18N_APP_NAME = 'guifinetstudio'|I18N_APP_NAME = 'guifinet-studio'|" $SRC_DIR/utils.py | sed "s|LOCALE_DIR = 'locale'|LOCALE_DIR = '/usr/share/locale'|" > $DST_DIR/usr/share/pyshared/guifinet-studio/utils.py

for l in $LOCALES
do
	mkdir -p "$DST_DIR/usr/share/locale/$l/LC_MESSAGES" && msgfmt $SRC_DIR/locale/$l.po -o "$DST_DIR/usr/share/locale/$l/LC_MESSAGES/guifinet-studio.mo"
done

#BUILD!
fakeroot dpkg --build $DST_DIR guifinet-studio_0.7-1_all.deb
