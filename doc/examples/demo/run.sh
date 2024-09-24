

mkdir src
ls
run-if --dependency src/ --target build.sh touch build.sh
ls
run-if --sentinal build.sh  rm build.sh


