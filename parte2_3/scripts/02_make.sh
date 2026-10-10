. "$(dirname "$0")/_comun.sh"
cmd 'make clean'
cmd 'make'
cmd 'ls -l lab12'
cmd './lab12 || test $? -eq 1'
