When two branches are edited differently and are later merged, a merge
conflict is produced by Git whenever the same lines have been changed
in both, because the tool cannot determine on its own which version
should be kept without a person's help. The affected file is marked
with conflict markers that must be resolved before the merge can be
completed, and until they are resolved the repository is left in a
state that is neither fully merged nor fully separate. A person
encountering this for the first time is often confused by the markers
themselves, because it is not immediately understood that the text
between them represents two competing versions of the same change,
rather than two unrelated pieces of writing that happen to sit next to
each other in the file. Once a version has been chosen or written by
hand, the file is staged and the merge is completed by a commit that
is recorded with two parent commits instead of the usual one, a
detail that is easily missed by someone who has only ever produced
ordinary, single-parent commits before a real conflict is met.
