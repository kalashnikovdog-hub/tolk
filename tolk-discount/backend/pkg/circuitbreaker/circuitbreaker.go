package circuitbreaker

import (
	"errors"
	"sync"
	"time"
)

var (
	ErrCircuitOpen = errors.New("circuit breaker is open")
	ErrServiceUnavailable = errors.New("service unavailable")
)

type State int

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

type Config struct {
	MaxFailures      int
	Timeout          time.Duration
	HalfOpenRequests int
	MetricsWindow    time.Duration
}

type CircuitBreaker struct {
	mu               sync.RWMutex
	state            State
	failures         int
	lastFailure      time.Time
	halfOpenRequests int
	config           Config
	successCount     int
	totalRequests    int64
	failureCount     int64
}

func New(config Config) *CircuitBreaker {
	return &CircuitBreaker{
		state:  StateClosed,
		config: config,
	}
}

func (cb *CircuitBreaker) Execute(work func() error) error {
	cb.mu.Lock()
	
	if cb.state == StateOpen {
		if time.Since(cb.lastFailure) > cb.config.Timeout {
			cb.state = StateHalfOpen
			cb.halfOpenRequests = cb.config.HalfOpenRequests
		} else {
			cb.mu.Unlock()
			cb.totalRequests++
			cb.failureCount++
			return ErrCircuitOpen
		}
	}
	
	cb.totalRequests++
	cb.mu.Unlock()
	
	err := work()
	
	cb.mu.Lock()
	defer cb.mu.Unlock()
	
	if err != nil {
		cb.failures++
		cb.lastFailure = time.Now()
		cb.failureCount++
		
		if cb.failures >= cb.config.MaxFailures {
			cb.state = StateOpen
		}
		
		if cb.state == StateHalfOpen {
			cb.halfOpenRequests--
			if cb.halfOpenRequests <= 0 {
				cb.state = StateOpen
			}
		}
		
		return err
	}
	
	cb.successCount++
	cb.failures = 0
	
	if cb.state == StateHalfOpen {
		cb.halfOpenRequests--
		if cb.halfOpenRequests <= 0 {
			cb.state = StateClosed
		}
	}
	
	return nil
}

func (cb *CircuitBreaker) State() State {
	cb.mu.RLock()
	defer cb.mu.RUnlock()
	return cb.state
}

func (cb *CircuitBreaker) Stats() map[string]interface{} {
	cb.mu.RLock()
	defer cb.mu.RUnlock()
	
	return map[string]interface{}{
		"state":            cb.state.String(),
		"failures":         cb.failures,
		"success_count":    cb.successCount,
		"total_requests":   cb.totalRequests,
		"failure_count":    cb.failureCount,
		"last_failure":     cb.lastFailure,
	}
}

func (s State) String() string {
	switch s {
	case StateClosed:
		return "closed"
	case StateOpen:
		return "open"
	case StateHalfOpen:
		return "half-open"
	default:
		return "unknown"
	}
}
