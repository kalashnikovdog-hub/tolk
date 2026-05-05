.PHONY: dev dev-backend dev-frontend install-frontend install-all

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Install root dependencies (concurrently)
install-root:
	npm install

# Install all dependencies
install-all: install-root install-frontend

# Run both backend and frontend in development mode
dev:
	npm run dev

# Run backend only
dev-backend:
	cd backend && make dev

# Run frontend only
dev-frontend:
	cd frontend && npm run dev
