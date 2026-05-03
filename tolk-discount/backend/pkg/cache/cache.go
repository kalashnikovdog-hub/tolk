package cache

import (
	"context"
	"encoding/json"
	"time"

	"github.com/redis/go-redis/v9"
)

type Cache struct {
	client *redis.Client
	prefix string
}

type Config struct {
	Client     *redis.Client
	KeyPrefix  string
}

func New(config Config) *Cache {
	return &Cache{
		client: config.Client,
		prefix: config.KeyPrefix,
	}
}

func (c *Cache) Get(ctx context.Context, key string, dest interface{}) error {
	fullKey := c.prefix + ":" + key
	
	data, err := c.client.Get(ctx, fullKey).Bytes()
	if err != nil {
		return err
	}
	
	return json.Unmarshal(data, dest)
}

func (c *Cache) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	fullKey := c.prefix + ":" + key
	
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	
	return c.client.Set(ctx, fullKey, data, ttl).Err()
}

func (c *Cache) Delete(ctx context.Context, key string) error {
	fullKey := c.prefix + ":" + key
	return c.client.Del(ctx, fullKey).Err()
}

func (c *Cache) Exists(ctx context.Context, key string) (bool, error) {
	fullKey := c.prefix + ":" + key
	
	result, err := c.client.Exists(ctx, fullKey).Result()
	if err != nil {
		return false, err
	}
	
	return result > 0, nil
}

func (c *Cache) GetOrSet(ctx context.Context, key string, ttl time.Duration, loader func() (interface{}, error)) (interface{}, error) {
	exists, err := c.Exists(ctx, key)
	if err != nil {
		return nil, err
	}
	
	if exists {
		var data []byte
		fullKey := c.prefix + ":" + key
		data, err = c.client.Get(ctx, fullKey).Bytes()
		if err != nil {
			return nil, err
		}
		
		var value interface{}
		if err := json.Unmarshal(data, &value); err != nil {
			return nil, err
		}
		return value, nil
	}
	
	value, err := loader()
	if err != nil {
		return nil, err
	}
	
	if err := c.Set(ctx, key, value, ttl); err != nil {
		return nil, err
	}
	
	return value, nil
}

func (c *Cache) Increment(ctx context.Context, key string, amount int64) (int64, error) {
	fullKey := c.prefix + ":" + key
	return c.client.IncrBy(ctx, fullKey, amount).Result()
}

func (c *Cache) Decrement(ctx context.Context, key string, amount int64) (int64, error) {
	fullKey := c.prefix + ":" + key
	return c.client.DecrBy(ctx, fullKey, amount).Result()
}

func (c *Cache) Expire(ctx context.Context, key string, ttl time.Duration) error {
	fullKey := c.prefix + ":" + key
	return c.client.Expire(ctx, fullKey, ttl).Err()
}

func (c *Cache) Ping(ctx context.Context) error {
	return c.client.Ping(ctx).Err()
}
