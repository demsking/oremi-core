#!/bin/bash

# oddly the python pre-commit hook doesn't actually install things during install
# here's a hack to force ruff into the pre-commit cache (works but is not great)
pre-commit run

# pre-commits output is a bit verbose when it succeeds, choose your own output wrangling
patch=$(autoPatchelf ~/.cache/pre-commit/)
if [[ $? -ne 0 ]]; then
  echo "$patch"
  exit 1
else
  echo "patched ~/.cache/pre-commit"
fi
