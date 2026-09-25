# What a commit holds

A commit in Git is a labeled snapshot of your whole project at one
moment. It records the state of every file Git tracks, not just the
lines that changed since the previous commit. A commit also stores
the author, the committer, a timestamp for each, a message
describing what was done and why, and a pointer back to the commit
before it, its parent commit. The first commit in a repository has no
parent.

Before a change becomes part of a commit, it passes through an
intermediate area called the staging area, or the index. The command
`git add` copies the current content of a file from your working
folder into the staging area. `git commit` records the staged
content, not necessarily whatever is sitting on disk at that time.
This is a common point of confusion for people who are new to Git:
if you stage a file and then keep editing it, those later edits are
not included in the next commit unless you stage the file again.
Running `git status` before you commit lists such a file twice, once
as staged and once as modified, so you can check what is about to be
recorded.
