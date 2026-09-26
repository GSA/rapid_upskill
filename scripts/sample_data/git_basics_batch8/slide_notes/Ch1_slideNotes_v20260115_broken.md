# Chapter 1: Git Basics for New Team Members

## Slide 1: What Version Control Solves
- A shared history records who changed which file, and when, across the whole project.
- Version control lets a team recover an earlier state instead of losing work to an overwritten file.
- Every change is tracked as one discrete, reviewable step, never a silent overwrite.

**Presenter Script:**
Before version control, many teams tracked a project's history by hand,
often by renaming a folder or a file every time something important
changed. That approach breaks down quickly, because nobody can reliably
say which copy is current, why a change was made, or whether it is safe
to go back to an earlier version. Version control replaces that
guesswork with one shared history that every tracked file in the
project follows together. Each recorded change, called a commit,
captures the exact state of every tracked file at that moment, along
with a short message explaining what changed and why it changed.
Because that history grows one step at a time, nothing already recorded
is silently overwritten. An earlier state is always still there, ready
to be recovered if a later change turns out to be wrong. For a new team
member, this same history doubles as a teaching tool. Reading through
it in order shows how the project actually reached its current shape,
one deliberate step after another, instead of leaving that story to
guesswork or half-remembered conversation. The rest of this chapter
builds directly on that one idea: a shared, ordered, and recoverable
history of every change.

## Slide 2: Recording Your First Change
- `git status` shows which tracked files changed since the last recorded snapshot.
- `git add` stages exactly the changes that belong in the next snapshot.
- `git commit` writes a new snapshot, with a message describing what changed and why.
- A commit stays local until it is deliberately shared with a remote repository.
- Small, frequent commits are easier to review, explain, and undo than one large commit.

**Presenter Script:**
Recording a change is a small sequence of deliberate steps. First,
git status shows what changed. Next, git add stages exactly the
changes that belong in the next snapshot. Finally, git commit writes
the staged changes as a new snapshot, with a short message describing
what changed and why. The commit stays local until it is shared with
a remote repository.

References:
- A synthetic training note on commit-message conventions, prepared for this guide's own running example.
- A synthetic team style guide entry on keeping commits small and reviewable.
