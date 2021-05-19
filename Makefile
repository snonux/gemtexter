all: generate
generate:
	git submodule init
	git submodule update
	bash ./buetow.org.sh --generate
publish:
	USE_GIT=yes ./buetow.org.sh --generate
	git commit -a
	git push
test: shellcheck
	LOG_VERBOSE=yes ./buetow.org.sh --test
shellcheck:
	shellcheck \
		--norc \
		--external-sources \
		--check-sourced \
		--exclude=SC2155,SC2010,SC2154,SC1090,SC2012 \
		buetow.org.sh
