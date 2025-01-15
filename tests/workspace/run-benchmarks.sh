set -e
rm _* -rf

args="--levels 1 --files-per-level 1000 --dirs-per-level 3 --file-size 100000"
root="_test1"
echo "One Level/Big files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"


args="--levels 5 --files-per-level 1000 --dirs-per-level 3 --file-size 1"
root="_test2"
echo "Many Level/Small files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"




args="--levels 5 --files-per-level 1000 --dirs-per-level 3 --file-size 100000"
root="_test3"
echo "Many Level/Big files"
echo "========="
echo ${args}
python make-large-dir.py --root-name ${root} ${args}
echo "Size $(du -hs ${root}*)"
echo "Number of files $(fd . -t f ${root}-* | wc -l)"
echo Rust
rm .run-if.json -f
hyperfine -- "cargo run -- -d ${root}-* -t missing echo hi"
echo Python
rm .run-if.json -f
hyperfine -- "run-if --dependency ${root}-* --target missing echo hi"


