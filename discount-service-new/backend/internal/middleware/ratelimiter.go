package middleware

import (
	"context"
	"fmt"
	"net/http"
	"strconv"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

type RateLimiter struct {
	client  *redis.Client
	requests map[string]*RequestCounter
	mu       sync.RWMutex
	limit    int
	window   time.Duration
}

type RequestCounter struct {
	count     int
	resetTime time.Time
}

func RateLimiter(redisAddr string) func(http.Handler) http.Handler {
	client := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})
	
	limiter := &RateLimiter{
		client:   client,
		requests: make(map[string]*RequestCounter),
		limit:    100,
		window:   time.Minute,
	}
	
	return limiter.middleware
}

func (rl *RateLimiter) middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		clientIP := getClientIP(r)
		
		if !rl.Allow(clientIP) {
			w.Header().Set("Content-Type", "application/json")
			w.Header().Set("Retry-After", strconv.Itoa(int(rl.window.Seconds())))
			w.Header().Set("X-RateLimit-Limit", strconv.Itoa(rl.limit))
			w.Header().Set("X-RateLimit-Remaining", "0")
			w.WriteHeader(http.StatusTooManyRequests)
			fmt.Fprintf(w, `{"error":"rate limit exceeded","retry_after":%d}`, int(rl.window.Seconds()))
			return
		}
		
		next.ServeHTTP(w, r)
	})
}

func (rl *RateLimiter) Allow(key string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	redisKey := "ratelimit:" + key
	
	current, err := rl.client.Incr(ctx, redisKey).Result()
	if err != nil {
		return true
	}
	
	if current == 1 {
		rl.client.Expire(ctx, redisKey, rl.window)
	}
	
	remaining := rl.limit - int(current)
	if remaining < 0 {
		remaining = 0
	}
	
	ttl, _ := rl.client.TTL(ctx, redisKey).Result()
	
	return current <= int64(rl.limit)
}

func getClientIP(r *http.Request) string {
	forwarded := r.Header.Get("X-Forwarded-For")
	if forwarded != "" {
		return forwarded
	}
	
	realIP := r.Header.Get("X-Real-IP")
	if realIP != "" {
		return realIP
	}
	
	return r.RemoteAddr
}
