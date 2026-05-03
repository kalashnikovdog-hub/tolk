package middleware

import (
	"fmt"
	"net/http"
	"runtime"
	"strings"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "path", "status"},
	)

	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)

	httpRequestsInFlight = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "http_requests_in_flight",
			Help: "Number of HTTP requests currently being processed",
		},
	)

	goRoutines = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "go_goroutines",
			Help: "Number of Go routines",
		},
	)

	memoryUsage = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "go_memory_usage_bytes",
			Help: "Memory usage in bytes",
		},
		[]string{"type"},
	)
)

func PrometheusMetricsHandler() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		updateGoMetrics()
		promhttp.Handler().ServeHTTP(w, r)
	}
}

func PrometheusMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		
		httpRequestsInFlight.Inc()
		defer httpRequestsInFlight.Dec()
		
		wrapped := &responseWriterWithStatus{ResponseWriter: w, status: http.StatusOK}
		
		next.ServeHTTP(wrapped, r)
		
		duration := time.Since(start).Seconds()
		
		method := r.Method
		path := sanitizePath(r.URL.Path)
		status := fmt.Sprintf("%d", wrapped.status)
		
		httpRequestsTotal.WithLabelValues(method, path, status).Inc()
		httpRequestDuration.WithLabelValues(method, path).Observe(duration)
	})
}

func updateGoMetrics() {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	
	goRoutines.Set(float64(runtime.NumGoroutine()))
	memoryUsage.WithLabelValues("alloc").Set(float64(m.Alloc))
	memoryUsage.WithLabelValues("sys").Set(float64(m.Sys))
	memoryUsage.WithLabelValues("heap_alloc").Set(float64(m.HeapAlloc))
}

func sanitizePath(path string) string {
	if path == "" {
		return "root"
	}
	
	path = strings.ReplaceAll(path, "/", "_")
	path = strings.TrimPrefix(path, "_")
	
	if len(path) > 50 {
		path = path[:50]
	}
	
	return path
}

type responseWriterWithStatus struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriterWithStatus) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}
