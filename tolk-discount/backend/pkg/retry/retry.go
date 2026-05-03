package retry

import (
	"context"
	"math"
	"math/rand"
	"time"
)

type Config struct {
	MaxRetries      int
	InitialInterval time.Duration
	MaxInterval     time.Duration
	Multiplier      float64
	RandomFactor    float64
}

func DefaultConfig() Config {
	return Config{
		MaxRetries:      5,
		InitialInterval: 1 * time.Second,
		MaxInterval:     30 * time.Second,
		Multiplier:      2.0,
		RandomFactor:    0.1,
	}
}

type Operation func() error

func WithRetry(ctx context.Context, op Operation, config Config) error {
	var lastErr error
	
	for attempt := 0; attempt <= config.MaxRetries; attempt++ {
		if err := op(); err == nil {
			return nil
		} else {
			lastErr = err
		}
		
		if attempt >= config.MaxRetries {
			break
		}
		
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(calculateBackoff(attempt, config)):
		}
	}
	
	return lastErr
}

func calculateBackoff(attempt int, config Config) time.Duration {
	multiplier := math.Pow(config.Multiplier, float64(attempt))
	interval := float64(config.InitialInterval) * multiplier
	
	if interval > float64(config.MaxInterval) {
		interval = float64(config.MaxInterval)
	}
	
	jitter := interval * config.RandomFactor * rand.Float64()
	
	return time.Duration(interval + jitter)
}

func WithExponentialBackoff(ctx context.Context, op Operation, maxRetries int, initialDelay time.Duration) error {
	config := Config{
		MaxRetries:      maxRetries,
		InitialInterval: initialDelay,
		MaxInterval:     30 * time.Second,
		Multiplier:      2.0,
		RandomFactor:    0.1,
	}
	
	return WithRetry(ctx, op, config)
}
