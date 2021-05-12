all: generate
generate:
	bash ./buetow.org.sh --generate
publish:
	ADD_GIT=yes ./buetow.org.sh --generate
	git commit -a
	git push
test: shellcheck
	./buetow.org.sh --test
shellcheck:
	shellcheck \
		--norc \
		--external-sources \
		--check-sourced \
		--exclude=SC2155,SC2010,SC2154,SC1090 \
		buetow.org.sh
