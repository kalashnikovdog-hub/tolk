.PHONY: build run test clean docker-build docker-run

build:
	go build -o bin/main ./cmd/main.go

run:
	go run ./cmd/main.go

test:
	go test -v -race -cover ./...

clean:
	rm -rf bin/
	go clean

docker-build:
	docker build -t discount-hub-api:latest .

docker-run:
	docker run -p 8080:8080 --env-file .env discount-hub-api:latest

dev:
	go run -race ./cmd/main.go

lint:
	golangci-lint run

fmt:
	go fmt ./...

vet:
	go vet ./...

generate:
	protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative \
		proto/*.proto
