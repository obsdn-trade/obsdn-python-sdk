.PHONY: setup lint test test.staging build check clean

PY := .venv/bin/python

setup:
	uv venv
	uv pip install -e ".[dev]"

lint:
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

test:
	$(PY) -m pytest tests/ -q --ignore=tests/test_e2e_staging.py --ignore=tests/test_ws_staging.py

# Hits live staging. Needs OBSDN_TEST_API_KEY/SECRET/SIGNER_KEY; skips without them.
test.staging:
	$(PY) -m pytest tests/test_e2e_staging.py tests/test_ws_staging.py -q

# Wheel must ship obsdn/py.typed, else downstream type checkers ignore our annotations.
build:
	rm -rf dist/
	uv build --wheel
	@$(PY) -c "import zipfile,glob; \
		n = zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist(); \
		assert 'obsdn/py.typed' in n, 'py.typed missing from wheel'; \
		print('wheel OK, py.typed present')"

check: lint test build

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache
