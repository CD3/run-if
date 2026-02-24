  $ $TESTDIR/../../target/debug/run-if -d dep2.txt echo HI
  Error: dependency 'dep2.txt' does not exist.
  [1]
  $ mkdir deps
  $ $TESTDIR/../../target/debug/run-if -d deps/dep1.txt echo HI
  Error: dependency 'deps/dep1.txt' does not exist.
  [1]
  $ $TESTDIR/../../target/debug/run-if -d deps echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if -d deps echo HI
  $ mkdir deps/l1
  $ $TESTDIR/../../target/debug/run-if -d deps echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if -d deps echo HI
  $ $TESTDIR/../../target/debug/run-if -d deps ech HI
  
  thread 'main' * panicked * (glob)
  Error * Command parts: ["ech", "HI"]* (glob)
  note: run * (glob)
  [101]
