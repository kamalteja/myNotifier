all: docker_build

build:
	docker-compose -f docker/docker-compose.yaml build

install:
	pip install -e .