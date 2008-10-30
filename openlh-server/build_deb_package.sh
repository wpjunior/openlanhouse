#!/bin/bash
./autogen.sh $@
dpkg-buildpackage -rfakeroot