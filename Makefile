PYTHON ?= python3
OUT_DIR ?= results/generated

.PHONY: all test analyze legacy-plots clean

all: test analyze

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(PYTHON) -m py_compile analysis/analyze_saved_bitstreams.py

analyze:
	mkdir -p $(OUT_DIR)
	$(PYTHON) analysis/analyze_saved_bitstreams.py

legacy-plots:
	cd baseline_covertChannel && \
		$(PYTHON) scripts/analyze_bits.py
	cd baseline_covertChannel && \
		$(PYTHON) scripts/plot_repeats.py
	cd baseline_covertChannel && \
		$(PYTHON) scripts/plot_modulation.py

clean:
	rm -rf \
		__pycache__ \
		analysis/__pycache__ \
		tests/__pycache__ \
		$(OUT_DIR)
