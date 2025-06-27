# ───────────────────────────────────────────────────────────────
# Stage 1 — Build
# ───────────────────────────────────────────────────────────────
FROM golang:1.21 AS builder

WORKDIR /app

# Copy go.mod and go.sum to leverage Go caching
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -o provider-service .
# ───────────────────────────────────────────────────────────────
# Stage 2 — Runtime (distroless or scratch could be used too)
# ───────────────────────────────────────────────────────────────
FROM debian:bullseye-slim

LABEL maintainer="Caleb Wheeler <caleb.li.wheeler@gmail.com>"

# Minimal necessary packages for TLS, etc.
RUN apt-get update && apt-get install -y \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user (recommended for container security)
RUN useradd -m appuser

WORKDIR /app
COPY --from=builder /app/provider-service .

USER appuser

# Expose HTTP port
EXPOSE 8080

# Run the server
ENTRYPOINT ["./provider-service"]
