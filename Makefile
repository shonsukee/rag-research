rag:
	python -m lib.rag.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-dir $(prompt-dir)

# ex:
# make rag name=switchbot types=commit out=./result prompt-dir=./lib/rag

llm:
	python -m lib.llm.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-dir $(prompt-dir)

# ex:
# make llm name=switchbot types=commit out=./result prompt-dir=./lib/llm

duplicate:
	python -m lib.duplicate_rag.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-dir $(prompt-dir)

# ex:
# make duplicate name=switchbot types=commit out=./result prompt-dir=./lib/duplicate_rag

store:
	python -m lib.store.main --namespace $(name) --version $(version) --method $(method)
# ex:
# make store name=switchbot version=latest method=all