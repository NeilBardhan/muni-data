.DEFAULT_GOAL := help
SHELL := bash

version := 0.1.0

.PHONY: help
help:  ## Print this help message.
	@grep -h '\s##\s' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' \
	| sort -k1

.PHONY: poetry
POETRY_USE_PYTHON ?=
poetry: install-poetry poetry.lock ## Create or update a Poetry-based development environment.
	@$(call i, Installing project plus its run time and development requirements...)
	[ -z "$(POETRY_USE_PYTHON)" ] || poetry env use "$(POETRY_USE_PYTHON)"
	poetry install
	@$(call i, Poetry setup and installation complete. Run '. .venv/bin/activate' to activate.)

.PHONY: install-poetry
install-poetry: ## Install poetry if not already present.
	$(call i, Installing Poetry...)
	curl -sSL https://install.python-poetry.org | python3 -
	poetry --version

poetry.lock: pyproject.toml poetry.toml ## Create or update the lock file.
	@$(call i, Updating poetry.lock file...)
	poetry check --lock || poetry lock

.PHONY: poetry.toml
POETRY_ALWAYS_COPY ?= false
poetry.toml:  ## Create or update local Poetry configuration
	@$(call i, Configuring poetry...)
	[ -f poetry.toml ] || touch poetry.toml
	grep 'virtualenvs.create' < poetry.toml || poetry config --local virtualenvs.create true
	grep 'virtualenvs.in-project' < poetry.toml || poetry config --local virtualenvs.in-project true
	grep 'virtualenvs.options.always-copy = true' < poetry.toml \
		|| poetry config --local virtualenvs.options.always-copy $(POETRY_ALWAYS_COPY)

##############
# Versioning #
##############

.PHONY: bump-patch
bump-patch: ## Bump the patch version (_._.X) everywhere it appears in the project.
	@$(call i, Bumping the patch number)
	bump2version patch --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-minor
bump-minor: ## Bump the minor version (_.X._) everywhere it appears in the project.
	@$(call i, Bumping the minor number)
	bump2version minor --verbose --config-file config/.bumpversion.cfg

.PHONY: bump-major
bump-major: ## Bump the major version (X._._) everywhere it appears in the project.
	@$(call i, Bumping the major number)
	bump2version major --verbose --config-file config/.bumpversion.cfg

##############
# Tests.     #
##############

.PHONY: test
test: ## Run unit tests.
	@$(call i, Running tests...)
	poetry run pytest -c=config/pytest.ini