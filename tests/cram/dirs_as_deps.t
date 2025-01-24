# make sure that changes to files in directories
# and sub-directories trigger a run.
  $ mkdir -p dep/dir
  $ touch dep/f1.txt
  $ touch dep/f2.txt
  $ touch dep/dir/f1.txt
  $ touch dep/dir/f2.txt
  $ run-if -d dep echo HI
  HI
  $ run-if -d dep echo HI
  $ echo a > dep/f1.txt
  $ run-if -d dep echo HI
  HI
  $ echo a > dep/f1.txt
  $ run-if -d dep echo HI
  $ echo a > dep/dir/f1.txt
  $ run-if -d dep echo HI
  HI
  $ echo a > dep/dir/f1.txt
  $ run-if -d dep echo HI
  $ echo b > dep/dir/f1.txt
  $ run-if -d dep echo HI
  HI
