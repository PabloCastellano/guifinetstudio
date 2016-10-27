# Guifi.net Studio

GSoC 2012 project

More information is available here:
http://en.wiki.guifi.net/wiki/User:Pablog/GSoC2012/Guifi.net%20Studio

You can check out the main development branch from GitHub at:
https://github.com/PabloCastellano/guifinetstudio

# Dependences

In order to run Guifi.net Studio, you need to install the following packages:
* Python
* Gtk Champlain (and GObject Introspection)
* Git (necessary only if you want to deal with the repository)

Under Ubuntu 12-14 (and surely most of the Ubuntu derivates) you can simply run:

    sudo apt-get install python2.7 gir1.2-gtkchamplain-0.12 gir1.2-gtkclutter-1.0
    sudo pip install libcnml

Optional:

    sudo apt-get install git python-lxml python-kml python-twisted-core python-jinja2 python-geopy

* git: Only necessary if you want to download Guifi.net Studio and deal with its repository
* python-lxml: it's faster than the default XML API. It's recommended and used if available
* python-kml: Only necessary if you want to export CNML to KML format
* python-geopy: Enables calculating distances between nodes

# Arch Linux

To be able to run this application into Arch Linux distribution system you
should install the dependences:

    $ pacman -Sy libchamplain

To run the application use the python interpreter version 2.7 instead of
3 that is provided by default in this distribution:

    $ python2.7 guifinet_studio.py

# Bugs

Please, report bugs using [GitHub issues](https://github.com/PabloCastellano/guifinetstudio/issues).

# Patches

You can clone the repository and submit patches through the GitHub interface:

1. Login at GitHub
2. Go to https://github.com/PabloCastellano/guifinetstudio and "Fork"
3. Go to your own new Guifi.net Studio repository in GitHub
4. Clone it -> make your changes -> commit & push
5. Press "Request merge" in the right column and fill in the fields

You don't need to create an issue for it. Just submit your merge request.

# Translations

Guifi.net Studio uses gettext() so that it can be easily translated into other languages

If you want to help with internationalization/localization (i18n/l10n) have a look at:
https://www.transifex.com/projects/p/guifinetstudio/

You can also use the following Guifi.net mailing list where we coordinate translations:
https://llistes.guifi.net/sympa/info/guifi-i18n
guifi-i18n@llistes.guifi.net

### Generate .pot file:

    xgettext --language=Python --keyword=_ --output=locale/guifinetstudio.pot champlainguifinet.py configmanager.py guifinet_studio.py ui.py unsolclic.py utils.py
    xgettext -j --language=Glade --output=locale/guifinetstudio.pot ui/*.ui

### Compile es.po:

    mkdir -p es/LC_MESSAGES && msgfmt es.po -o es/LC_MESSAGES/guifinetstudio.mo

# Building Debian Package

Run the following commands from the root directory:

    sudo apt-get install cdbs quilt
    export QUILT_PATCHES=debian/patches
    dpkg-buildpackage -rfakeroot -k463F919C

Don't forget to replace -k with your own PGP key ID or remove the parameter to leave the package unsigned.

# Install from source

    git clone https://github.com/PabloCastellano/guifinetstudio.git
    cd guifinetstudio
    mkvirtualenv --system-site-packages guifinetstudio
    pip install -r requirements.txt
    python setup.py develop
    ./guifinet-studio
