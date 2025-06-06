  $ echo "HI" > dep1.txt
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt ls missing
  ls: cannot access 'missing': No such file or directory
  [1]
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt ls missing
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -u ls missing
  ls: cannot access 'missing': No such file or directory
  [1]
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -u ls missing
  ls: cannot access 'missing': No such file or directory
  [1]
  $ touch missing
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -u ls missing
  missing
  $ $TESTDIR/../../target/debug/run-if -d dep1.txt -u ls missing
