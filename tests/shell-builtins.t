  $ alias lll
  /bin/bash: line 2: alias: lll: not found
  [1]
  $ run-if == alias lll == output
  Error running command: [Errno 2] No such file or directory: 'alias'
  [127]
  $ run-if --shell == alias lll == output
  alias: lll not found
  [1]
