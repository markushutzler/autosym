#!/bin/sh

if [ ! -d library/.git ]
then
	echo "Cloning autosym-library.git"
	git clone https://github.com/markushutzler/autosym-library.git library
else
	echo "Updating autosym-library.git"
	cd library
	git pull
	cd ..
fi

echo "Running autosym"
autosym library output
