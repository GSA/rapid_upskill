---
chapter: 1
title: "Chapter 1: Snapshots, history and branches"
---

# Chapter 1: Snapshots, history and branches

## Overview

This chapter introduces the idea at the center of Git: a commit is a
snapshot, not a list of edits. You build a commit on purpose, read the
project's history, and meet the branch and HEAD, the two ideas that let
more than one line of work exist at once.

## Learning Objectives

By the end of this chapter, you will be able to:

- Explain that a commit records a snapshot of the tracked files plus an
  author, a time, a message and a parent, rather than a list of edits.
- Build a commit deliberately by staging chosen changes and checking
  them before committing.
- Read the history and compare versions with git log and git diff,
  telling staged changes from unstaged ones.
- Describe a branch as a movable label on a commit and HEAD as the
  pointer that says where you are.

## Content

### A commit is a snapshot

A commit does not store a diff. It stores the tracked files as they
stood at that moment, plus an author, a time, a message and a link to
the commit before it. A file you did not touch still points to the
same stored content as the last commit. `git diff` works out a
difference on the spot by comparing two snapshots.

### Building a commit on purpose

I Do: watch one change staged and committed step by step: edit a file,
run `git add`, check `git status`, then run `git commit`.

We Do: stage a second change together, pausing before the commit so you
can check that `git status` shows only the file you meant to include.

You Do: make one more change alone, stage only that change, and commit
it with a message that says what changed and why.

### Reading the history

`git log` lists commits from newest to oldest. `git diff` compares your
working folder with the staging area; `git diff --staged` compares the
staging area with the last commit. Run both before you commit.

### Branches and HEAD

A branch is a movable label that points at one commit. HEAD is a
pointer that says which commit, and usually which branch, you are on.
Switching branches moves HEAD; a new commit moves the branch label
forward by one.

### Formative Check

Which statement about a commit is correct?

A. It stores only the lines changed since the last commit. Incorrect:
a commit stores the tracked files as they stood at that moment, not a
line-level diff.

B. It records a snapshot of the tracked files, plus an author, a time,
a message and a parent. Correct: this is the chapter's first
objective, and it is what `git diff` compares behind the scenes.

C. It is the same thing as a branch. Incorrect: a branch is a movable
label that points at a commit; the commit itself holds the snapshot.

D. It cannot have more than one parent. Incorrect: a merge commit has
two parents; this chapter does not cover merging.

## Key Concepts

- **Commit**: a snapshot of the tracked files, with an author, a time,
  a message and a parent.
- **Staging area**: where you assemble the next commit, filled by
  `git add`.
- **Branch**: a movable label that points at one commit.
- **HEAD**: the pointer that says which commit, and usually which
  branch, you are on.

## Assessment

This chapter's own check is the Formative Check above. A full
assessment for Chapter 1 draws further stems from the item bank once
the planned Stage 5 writes them.
