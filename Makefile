apr:
	python -m lib.apr.main --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)
# ex:
# make apr name=switchbot types=commit out=./result prompt-name=apr

llm:
	python -m lib.llm.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)

# ex:
# make llm name=switchbot types=commit out=./result prompt-name=llm

rag:
	python -m lib.rag.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)

# ex:
# make rag name=switchbot types=commit out=./result prompt-name=rag

db_rag:
	python -m lib.db_rag.apr --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)

# ex:
# make db name=switchbot types=commit out=./result prompt-name=db_rag

store:
	python -m lib.store.main --namespace $(name) --version $(version) --method $(method)
# ex:
# make store name=switchbot version=latest method=all