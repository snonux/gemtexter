all: generate
generate:
	bash ./buetow.org.sh --generate
publish:
	ADD_GIT=yes bash ./buetow.org.sh --generate
	bash -c 'git commit -a;exit 0'
	git push
