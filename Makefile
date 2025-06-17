apr:
	python -m lib.apr.main --namespace $(name) --data-types $(types) --output-dir $(out) --prompt-name $(prompt-name)
# ex:
# make apr name=switchbot types=commit out=./result prompt-name=apr

store:
	python -m lib.store.main --namespace $(name) --version $(version) --method $(method)
# ex:
# make store name=switchbot version=latest method=all