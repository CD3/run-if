  $ echo "HI" > dep1.txt
  $ echo "HI" > dep2.txt

don't run commands unless there is a reason
  $ "${CLI_EXE}" echo HI
  $ "${CLI_EXE}" echo HI

if a dependency is added, command should run once
  $ "${CLI_EXE}" echo HI -d dep1.txt
  HI
  $ "${CLI_EXE}" echo HI -d dep1.txt

if a target is added, command should run until it exists
  $ "${CLI_EXE}" echo HI -t missing
  HI
  $ "${CLI_EXE}" echo HI -t missing
  HI
  $ echo "HI" > missing
  $ "${CLI_EXE}" echo HI -t missing
  $ rm missing

  $ "${CLI_EXE}"
  No command given.
  $ "${CLI_EXE}" dep1.txt == echo HI == missing == missing2
  Error: too many argument groups. A maximum of 3 groups are allowed which means a maximum of 2 '==' delimiters are allowed.
  [1]
  $ "${CLI_EXE}" dep1.txt ==
  Error: detected argument groups, but command group is empty. There must be at least one argument after the first '==' delimiter.
  [1]
  $ "${CLI_EXE}" dep1.txt == echo HI
  $ "${CLI_EXE}" dep2.txt == echo HI
  HI
  $ "${CLI_EXE}" dep2.txt == echo HI
  $ "${CLI_EXE}" dep2.txt == echo HI == missing
  HI
  $ "${CLI_EXE}" dep2.txt == echo HI == missing
  HI
