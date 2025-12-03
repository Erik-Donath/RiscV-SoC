IMAGE_NAME := riscv
CONTAINER_NAME := riscv


.PHONY: build run clean help env


help:
	@echo "Commands:"
	@echo "  build    - Builds the whole Project"
	@echo "  env      - Creates a Development Environment with all necessary tools"
	@echo "  run      - Builds image (if needed) and runs the build steps"
	@echo "  clean    - Cleans up the Docker image"


build:
	docker build -t $(IMAGE_NAME) .


env:
	docker build --build-arg ENV=dev -t $(IMAGE_NAME) .
	docker run --rm -it -v "$(shell pwd)":/workspace --name $(CONTAINER_NAME) $(IMAGE_NAME)
	docker exec -it $(CONTAINER_NAME) sh -c "echo 'Hello World from the Docker'"

run: build
	docker run --rm -v "$(shell pwd)":/workspace --name $(CONTAINER_NAME) $(IMAGE_NAME) \
		sh -lc 'source ./env.sh && python3 cpu.py --build'


clean:
	docker rmi $(IMAGE_NAME)
