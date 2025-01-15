  $ echo "HI" > dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -- bash -c 'echo HI; touch target.txt'
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -- bash -c 'echo HI; touch target.txt'
  $ rm target.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -- bash -c 'echo HI; touch target.txt'
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -- bash -c 'echo HI; touch target.txt'
  $ echo "BYE" > dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -- bash -c 'echo HI; touch target.txt'
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -s sentinal.txt -- bash -c 'echo HI; touch target.txt'
  $ touch sentinal.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -s sentinal.txt -- bash -c 'echo HI; touch target.txt'
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -s sentinal.txt -- bash -c 'echo HI; touch target.txt'
  HI
  $ rm sentinal.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t target.txt -s sentinal.txt -- bash -c 'echo HI; touch target.txt'
