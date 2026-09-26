#!/bin/bash
# Preflight checks for the local Jev-plays-Factorio livestream (macOS).
# Prints one OK/MISSING line per requirement; exits 1 if anything is missing.
# Never prints secret values.
missing=0
check() { # check <label> <command...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "OK       $label";
  else echo "MISSING  $label"; missing=1; fi
}
check "macOS (this script is for the Mac)"        sw_vers
check "Python 3.10+"                               python3 -c 'import sys; assert sys.version_info >= (3,10)'
check "Docker reachable (Colima)"                  docker info
check "Colima running"                             colima status
check "FLE installed (fle CLI)"                    fle --help
check "Factorio app installed"                     test -d /Applications/factorio.app
check "OBS installed"                              test -d /Applications/OBS.app
check "TYPESAFE_API_KEY set (value not shown)"     test -n "$TYPESAFE_API_KEY"
if [ -f .env ] && grep -q '^TYPESAFE_API_KEY=.' .env; then
  echo "OK       .env contains TYPESAFE_API_KEY (value not shown)"
fi
if [ "$missing" -eq 0 ]; then echo "PREFLIGHT PASS"; else echo "PREFLIGHT FAIL - fix the MISSING lines above"; exit 1; fi
