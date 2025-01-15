  $ ls -a
  .
  ..
  $ echo "HI" > dep1.txt
  $ ls -a
  .
  ..
  dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI
  HI
  $ ls -a
  .
  ..
  .run-if.json
  dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI
  $ ls -a
  .
  ..
  .run-if.json
  dep1.txt
  $ echo "BYE" >> dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -f echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -t missing echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt echo HI

