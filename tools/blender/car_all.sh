#!/bin/sh
# Convert the named cars one after another and make each one's check sheet:  sh car_all.sh [fast] <id> [<id> ...]
# (run it from any folder that is NOT inside the downloaded models)
FAST=""; if [ "$1" = "fast" ]; then FAST="fast"; shift; fi
for c in "$@"; do
  echo "=== $c"
  "D:/blender/blender.exe" --background --python D:/crust-rush/source/tools/blender/car_convert.py -- "$c" $FAST 2>&1 | grep -E "^\[car|Error|Traceback|  File |assert" | grep -v "^\[car.*    [bhf]" | cut -c1-300
  D:/crust-rush/tools/py.cmd D:/crust-rush/source/tools/blender/car_sheet.py "$c"
done
