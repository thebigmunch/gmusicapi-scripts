## Submitting an issue

Bug reports and feature requests can be submitted to the [Issue Tracker](https://github.com/thebigmunch/gmusicapi-scripts/issues).

Some general guidelines to follow:

* Use an appropriate, descriptive title.
* Provide as many details as possible.
* Don't piggy-back. Keep separate topics in separate issues.

## Submitting code

Patches are welcome. Keep your code consistent with the rest of the project. [PEP8](https://www.python.org/dev/peps/pep-0008/) is a good guide, but with the following exceptions to keep in mind for coding/linting:

* Tabs should be used for indentation of code.
* Don't use line continuation that aligns with opening delimiter.
* I don't set a hard maximum line length. Instead, I try to keep line lengths as reasonable as possible without hurting readability nor ease of comprehension.

Some linter errors may need to be ignored to accommodate these differences.

For simple, single file changes/additions, sending or linking your modified file is acceptable. For complex, multiple file changes, creating a diff file or using GitHub's [Pull Request](https://help.github.com/articles/using-pull-requests/) feature is preferable.

If you have any questions or concerns, contact me through the methods listed below.

### Pull Requests

You should create a separate [feature branch][fb] in your [fork][fork] to commit your changes to. [Pull Requests](https://help.github.com/articles/creating-a-pull-request) will only be accepted if made from a [feature branch][fb] and against the [devel](https://github.com/thebigmunch/gmusicapi-scripts/tree/devel) branch of this repository.

Commit messages should be written in a [well-formed, consistent](https://sethrobertson.github.io/GitBestPractices/#usemsg) manner. See the [commit log](https://github.com/thebigmunch/gmusicapi-scripts/commits/devel) for acceptable examples.

Each commit should encompass the smallest logical changeset (e.g. changing two unrelated things in the same file would be two commits rather than one commit of "Change filename".) If you made a mistake in a commit in your Pull Request, you should [amend](https://www.atlassian.com/git/tutorials/rewriting-history/git-commit--amend) or [rebase](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase-i) to change your previous commit(s) then [force push](http://stackoverflow.com/a/12610763) to the [feature branch][fb] in your [fork][fork].

[fb]: https://help.github.com/articles/creating-and-deleting-branches-within-your-repository/#creating-a-branch
[fork]: https://help.github.com/articles/fork-a-repo

## Misc
For anything else, contact me by e-mail at <mail@thebigmunch.me> or on IRC in ``#gmusicapi`` on ``irc.freenode.net``
