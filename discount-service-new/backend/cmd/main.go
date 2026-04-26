package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/discount-hub/api-gateway/internal/config"
	"github.com/discount-hub/api-gateway/internal/middleware"
	"github.com/discount-hub/api-gateway/pkg/cache"
	"github.com/discount-hub/api-gateway/pkg/circuitbreaker"
	"github.com/redis/go-redis/v9"
)

func main() {
	cfg := config.Load()

	log.Printf("Starting API Gateway v2.0")
	log.Printf("Configuration loaded: port=%s, metrics=%v, tracing=%v", 
		cfg.Server.Port, cfg.Server.EnableMetrics, cfg.Server.EnableTracing)

	redisClient := initRedis(cfg)
	cacheStore := cache.New(cache.Config{
		Client:    redisClient,
		KeyPrefix: "gateway",
	})

	circuitBreaker := circuitbreaker.New(circuitbreaker.Config{
		MaxFailures:      cfg.Circuit.MaxFailures,
		Timeout:          cfg.Circuit.Timeout,
		HalfOpenRequests: cfg.Circuit.HalfOpenRequests,
		MetricsWindow:    cfg.Circuit.MetricsWindow,
	})

	mux := http.NewServeMux()

	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/ready", readinessHandler)
	
	if cfg.Server.EnableMetrics {
		mux.HandleFunc("/metrics", middleware.PrometheusMetricsHandler())
	}

	apiMux := http.NewServeMux()
	setupRoutes(apiMux, cfg, cacheStore, circuitBreaker)
	
	mux.Handle("/api/", middleware.Chain(
		middleware.Logging(),
		middleware.Recovery(),
		middleware.RateLimiter(cfg.Redis.Addr),
		middleware.CORS(),
	)(apiMux))

	server := &http.Server{
		Addr:         ":" + cfg.Server.Port,
		Handler:      mux,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
		MaxHeaderBytes: cfg.Server.MaxHeaderBytes,
	}

	go func() {
		log.Printf("Server listening on :%s", cfg.Server.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), cfg.Server.ShutdownTimeout)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server stopped gracefully")
}

func initRedis(cfg *config.Config) *redis.Client {
	client := redis.NewClient(&redis.Options{
		Addr:            cfg.Redis.Addr,
		Password:        cfg.Redis.Password,
		DB:              cfg.Redis.DB,
		PoolSize:        cfg.Redis.PoolSize,
		MinIdleConns:    cfg.Redis.MinIdleConns,
		MaxRetries:      cfg.Redis.MaxRetries,
		DialTimeout:     cfg.Redis.DialTimeout,
		ReadTimeout:     cfg.Redis.ReadTimeout,
		WriteTimeout:    cfg.Redis.WriteTimeout,
		PoolTimeout:     cfg.Redis.PoolTimeout,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := client.Ping(ctx).Err(); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	log.Println("Connected to Redis successfully")
	return client
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"healthy","timestamp":%d}`, time.Now().Unix())
}

func readinessHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, `{"status":"ready","timestamp":%d}`, time.Now().Unix())
}

func setupRoutes(mux *http.ServeMux, cfg *config.Config, cacheStore *cache.Cache, cb *circuitbreaker.CircuitBreaker) {
	mux.HandleFunc("/api/v1/discounts", handleDiscounts(cfg, cacheStore, cb))
	mux.HandleFunc("/api/v1/auth/login", handleLogin(cfg))
	mux.HandleFunc("/api/v1/auth/register", handleRegister(cfg))
}

func handleDiscounts(cfg *config.Config, cacheStore *cache.Cache, cb *circuitbreaker.CircuitBreaker) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		ctx := r.Context()
		
		var discounts []interface{}
		err := cb.Execute(func() error {
			return cacheStore.Get(ctx, "discounts:all", &discounts)
		})
		
		if err != nil {
			discounts = []interface{}{}
		}
		
		w.Header().Set("Content-Type", "application/json")
		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"data": discounts,
		})
	}
}

func handleLogin(cfg *config.Config) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		
		w.Header().Set("Content-Type", "application/json")
		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"message": "Login endpoint",
		})
	}
}

func handleRegister(cfg *config.Config) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		
		w.Header().Set("Content-Type", "application/json")
		jsonResponse(w, http.StatusOK, map[string]interface{}{
			"message": "Register endpoint",
		})
	}
}

func jsonResponse(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	
	encoder := json.NewEncoder(w)
	if err := encoder.Encode(data); err != nil {
		log.Printf("Failed to encode response: %v", err)
	}
}
