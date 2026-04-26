package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	Redis    RedisConfig
	NATS     NATSConfig
	JWT      JWTConfig
	Circuit  CircuitConfig
	Retry    RetryConfig
}

type ServerConfig struct {
	Port              string
	ReadTimeout       time.Duration
	WriteTimeout      time.Duration
	ShutdownTimeout   time.Duration
	MaxHeaderBytes    int
	EnableMetrics     bool
	EnableTracing     bool
}

type DatabaseConfig struct {
	DSN               string
	MaxOpenConns      int
	MaxIdleConns      int
	ConnMaxLifetime   time.Duration
	ConnMaxIdleTime   time.Duration
}

type RedisConfig struct {
	Addr              string
	Password          string
	DB                int
	PoolSize          int
	MinIdleConns      int
	MaxRetries        int
	DialTimeout       time.Duration
	ReadTimeout       time.Duration
	WriteTimeout      time.Duration
	PoolTimeout       time.Duration
}

type NATSConfig struct {
	URL               string
	Cluster           string
	MaxReconnect      int
	ReconnectWait     time.Duration
	Timeout           time.Duration
}

type JWTConfig struct {
	SecretKey         string
	AccessTokenExp    time.Duration
	RefreshTokenExp   time.Duration
	Issuer            string
}

type CircuitConfig struct {
	MaxFailures       int
	Timeout           time.Duration
	HalfOpenRequests  int
	MetricsWindow     time.Duration
}

type RetryConfig struct {
	MaxRetries        int
	InitialInterval   time.Duration
	MaxInterval       time.Duration
	Multiplier        float64
	RandomFactor      float64
}

func Load() *Config {
	return &Config{
		Server: ServerConfig{
			Port:            getEnv("SERVER_PORT", "8080"),
			ReadTimeout:     15 * time.Second,
			WriteTimeout:    15 * time.Second,
			ShutdownTimeout: 30 * time.Second,
			MaxHeaderBytes:  1 << 20,
			EnableMetrics:   getEnvBool("ENABLE_METRICS", true),
			EnableTracing:   getEnvBool("ENABLE_TRACING", true),
		},
		Database: DatabaseConfig{
			DSN:             getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/discounts?sslmode=disable"),
			MaxOpenConns:    getEnvInt("DB_MAX_OPEN_CONNS", 25),
			MaxIdleConns:    getEnvInt("DB_MAX_IDLE_CONNS", 5),
			ConnMaxLifetime: 5 * time.Minute,
			ConnMaxIdleTime: 5 * time.Minute,
		},
		Redis: RedisConfig{
			Addr:           getEnv("REDIS_URL", "localhost:6379"),
			Password:       getEnv("REDIS_PASSWORD", ""),
			DB:             0,
			PoolSize:       getEnvInt("REDIS_POOL_SIZE", 10),
			MinIdleConns:   getEnvInt("REDIS_MIN_IDLE_CONNS", 5),
			MaxRetries:     3,
			DialTimeout:    5 * time.Second,
			ReadTimeout:    3 * time.Second,
			WriteTimeout:   3 * time.Second,
			PoolTimeout:    4 * time.Second,
		},
		NATS: NATSConfig{
			URL:           getEnv("NATS_URL", "nats://localhost:4222"),
			Cluster:       getEnv("NATS_CLUSTER", "discount-cluster"),
			MaxReconnect:  10,
			ReconnectWait: 2 * time.Second,
			Timeout:       10 * time.Second,
		},
		JWT: JWTConfig{
			SecretKey:       getEnv("JWT_SECRET", "change-me-in-production"),
			AccessTokenExp:  15 * time.Minute,
			RefreshTokenExp: 7 * 24 * time.Hour,
			Issuer:          "discount-hub",
		},
		Circuit: CircuitConfig{
			MaxFailures:      5,
			Timeout:          30 * time.Second,
			HalfOpenRequests: 3,
			MetricsWindow:    60 * time.Second,
		},
		Retry: RetryConfig{
			MaxRetries:      5,
			InitialInterval: 1 * time.Second,
			MaxInterval:     30 * time.Second,
			Multiplier:      2.0,
			RandomFactor:    0.1,
		},
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}
