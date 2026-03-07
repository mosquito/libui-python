PYTHON ?= python

.PHONY: stubs lint format test clean patch screenshots

stubs: libui/core.pyi

libui/core.pyi: scripts/gen_stubs.py libui/core*.so
	$(PYTHON) scripts/gen_stubs.py > $@
	ruff format $@
	ruff check --fix $@

lint:
	ruff check libui/ scripts/

format:
	ruff format libui/ scripts/

test:
	$(PYTHON) -m pytest tests/

patch:
	$(PYTHON) scripts/apply_patches.py

screenshots:
	$(PYTHON) scripts/screenshots.py

clean:
	rm -f libui/core.pyi
