A merge conflict happens when two branches change identical lines in
different ways, and Git cannot tell on its own which version you want
to keep. Git stops the merge and marks the affected file instead of
finishing it for you. Inside the file, Git adds three markers: one
begins your side of the change, one separates your side from the
other side, and one ends the other side. This guide calls your side
"ours" and the other side "theirs", the same two words Git itself
prints in the file.

Worked example: your branch and a teammate's branch both change the
same line of a shared file, and you run the merge command to combine
the two branches. Git reports a conflict on that one file and keeps
the markers for you to read. You open the file, compare the "ours"
side against the "theirs" side, and decide which wording to keep,
sometimes combining both. You delete the three markers, save the
file, stage it, and finish the merge with a commit. That commit has
two parents, one from each branch, instead of the usual single
parent.

Now try it yourself: open a file with a marked conflict, compare both
sides against the change each branch made, choose the wording to
keep, then stage the file and commit the result.
