apr:
	python -m lib.apr.main --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)
# ex:
# make apr name=switchbot types=commit out=./result prompt-name=double

store:
	python -m lib.store.main --namespace $(name) --version $(version) --method $(method) --index-name $(index-name)
# ex:
# make store name=switchbot version=latest method=all index-name=latest
