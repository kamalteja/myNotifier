all: docker_build

docker_build:
	docker-compose -f docker/docker-compose.yaml build --no-cache

