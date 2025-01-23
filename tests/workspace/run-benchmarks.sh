set -e
rm _* -rf
rm .run-if.json -f

args="--levels 1 --files-per-level 1000 --dirs-per-level 3 --file-size 100000"
root="_test1-DO_NOT_SYNC"
echo "One Level/Big files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run --release -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"


args="--levels 3 --files-per-level 1000 --dirs-per-level 3 --file-size 1"
root="_test2-DO_NOT_SYNC"
echo "Multi-Level/Small files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run --release -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"




args="--levels 3 --files-per-level 1000 --dirs-per-level 3 --file-size 100000"
root="_test3-DO_NOT_SYNC"
echo "Multi-Level/Big files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run --release -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"


