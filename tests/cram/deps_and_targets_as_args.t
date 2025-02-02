  $ echo "HI" > dep1.txt
  $ echo "HI" > dep2.txt
  $ $TESTDIR/../../target/debug/run-if echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if echo HI
  $ $TESTDIR/../../target/debug/run-if echo HI -d dep1.txt
  HI
  $ $TESTDIR/../../target/debug/run-if echo HI -d dep1.txt
  $ $TESTDIR/../../target/debug/run-if
  No command given.
  $ $TESTDIR/../../target/debug/run-if dep1.txt == echo HI == missing == missing2
  Error: too many argument groups. A maximum of 3 groups are allowed which means a maximum of 2 '==' delimiters are allowed.
  [1]
  $ $TESTDIR/../../target/debug/run-if dep1.txt ==
  Error: detected argument groups, but command group is empty. There must be at least one argument after the first '==' delimiter.
  [1]
  $ $TESTDIR/../../target/debug/run-if dep1.txt == echo HI
  $ $TESTDIR/../../target/debug/run-if dep2.txt == echo HI
  HI
  $ $TESTDIR/../../target/debug/run-if dep2.txt == echo HI
  $ $TESTDIR/../../target/debug/run-if dep2.txt == echo HI == missing
  HI
  $ $TESTDIR/../../target/debug/run-if dep2.txt == echo HI == missing
  HI
