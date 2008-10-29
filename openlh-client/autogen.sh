#!/bin/sh
# Run this to generate all the initial makefiles, etc.

which gnome-autogen.sh || {
    echo "You need to install gnome-common from GNOME SVN and make"
    echo "sure the gnome-autogen.sh script is in your \$PATH."
    exit 1
}

REQUIRED_AUTOMAKE_VERSION=1.9 USE_GNOME2_MACROS=1 . gnome-autogen.sh $@
