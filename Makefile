
help:  ## Show help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clean autogenerated files
	rm -rf dist
	rm -rf .cache
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage
	git fetch --prune
	git gc --prune=now --aggressive
	rm -rf tmp
	rm -rf .cache
	rm -rf reports

setup: ## Setup the project
	git config --global http.sslVerify false
	pip install poetry
	poetry install --sync --only main
	pre-commit install-hooks
	pre-commit install

poetry-add: ## Add all packages from requirements.txt to poetry
	cat requirements.txt >> build_poetry.txt
	sed -i '/^#/d;/^$$/d' build_poetry.txt
	pip install poetry
	poetry add $$(cat build_poetry.txt)
	rm build_poetry.txt

format: ## Run pre-commit hooks
	pre-commit run -a

test: ## Run all tests
	pytest
