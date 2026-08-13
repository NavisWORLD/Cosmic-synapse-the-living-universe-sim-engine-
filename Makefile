.PHONY: test serve native

test:
	node --test packages/cosmic-synapse-universe-core/test/*.mjs
	python -m py_compile research/analysis/analyze_trials.py native/python/run_bridge.py native/python/cosmos_bridge/*.py

serve:
	node scripts/sync-engine.mjs
	python -m http.server 8080 -d apps/pwa

native:
	cmake -S native -B native/build
	cmake --build native/build --config Release
