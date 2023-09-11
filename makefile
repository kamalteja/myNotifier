all: build

build:
	docker-compose -f docker/docker-compose.yaml build

install:
# The -e flag will not install myNotifier in site-package
# rather, points to the app directory.
	pip install -e .

run: build
	docker-compose -f docker/docker-compose.yaml up
