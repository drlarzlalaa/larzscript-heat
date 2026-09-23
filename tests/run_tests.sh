#!/bin/sh
# Runs each tests/*.sh scenario and diffs its combined output against
# tests/<name>.expected. Same discipline as larzscript-superpowers.
#
# Env override: LZ="larzscript /path/to/heat.lz" to test another
# copy of the program (used by CI).
set -e
cd "$(dirname "$0")/.."
LZ="${LZ:-larzscript heat.lz}"
export LZ

pass=0; fail=0
for t in tests/*.sh; do
  case "$t" in *run_tests.sh) continue ;; esac
  exp="${t%.sh}.expected"
  got="$(sh "$t" 2>&1 || true)"   # scenarios may exit non-zero on purpose
  if [ "$got" = "$(cat "$exp")" ]; then
    pass=$((pass+1))
  else
    fail=$((fail+1)); echo "FAIL $t"; echo "--- expected ---"; cat "$exp"; echo "--- got ---"; echo "$got"
  fi
done
echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
