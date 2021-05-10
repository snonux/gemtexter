all: generate
generate:
	bash ./buetow.org.sh --generate
publish:
	ADD_GIT=yes bash ./buetow.org.sh --generate
	git commit -a
	git push
