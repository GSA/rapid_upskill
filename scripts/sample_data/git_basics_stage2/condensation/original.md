# What a commit holds

A commit in Git is a labeled snapshot of your whole project, taken at
one moment. It is not only a record of the lines that changed since
the previous commit; it is a snapshot of the state of every file
that Git is tracking. A commit also stores the name of the author
who wrote the change, the name of the committer who recorded it, a
timestamp for each of these two people, a short message describing
what was done and why, and a pointer back to the commit that came
before it, usually called its parent commit. The first commit in a
repository is a special case: it has no parent commit.

Before a change becomes part of a commit, it has to pass through an
intermediate area, commonly called the staging area, or sometimes
the index. The command `git add` copies the current content of a
file from your working folder into the staging area. It is the
staged content, not necessarily whatever happens to be sitting on
disk at that time, that the command `git commit` records. This is a
common point of confusion for people who are new to Git: if you
stage a file and then keep editing it, those later edits are not
included in the next commit unless you stage the file again. Running
`git status` before you commit lists such a file twice, once as
staged and once as modified, so you can check what is really about to
be recorded.
