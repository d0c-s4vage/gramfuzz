#!/bin/bash


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


cd $DIR/../tests


if [ $# -gt 1 ] ; then
	python -m unittest discover "$@"
else
	python -m unittest discover -p "test*.py"
fi
