hooksPath := $(git config --get core.hooksPath)

.PHONY: precommit sync check test lint
default: check

precommit:
ifneq ($(strip $(hooksPath)),.github/hooks)
	@git config --add core.hooksPath .github/hooks
endif
	$(MAKE) check
	$(MAKE) test

# The three commands below match docs/contributing/tooling.md exactly.
sync:
	python3 -B scripts/site/sync.py --write

check:
	python3 -B scripts/site/check.py

test:
	python3 -B scripts/tests/run_all.py

# tooling.md documents no lint command; these five tools are the ones this
# project has actually run and reported at the close of every batch. pylint
# is deliberately left out: it cannot run in this project's own environment
# (a missing astroid dependency), a standing, already-reported gap.
lint:
	black scripts
	isort scripts
	flake8 --max-line-length=88 scripts
	mypy --ignore-missing-imports scripts
	bandit -r scripts
