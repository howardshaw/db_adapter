# Executors Package

This package provides thread pool management for handling CPU-intensive tasks and sync operations in async context.

## Thread Pool Manager

The `ThreadPoolManager` class provides a managed thread pool executor with the following features:

- **Configurable worker count**: Defaults to `min(32, os.cpu_count() + 4)`
- **Lazy initialization**: Thread pool is created only when needed
- **Proper shutdown**: Clean shutdown with optional wait for completion
- **Thread naming**: Worker threads are named with prefix for easier debugging

## Usage

### Basic Usage

```python
from infras.executors import thread_pool, get_thread_pool

# Use the global thread pool
executor = get_thread_pool()

# Submit tasks
future = executor.submit(some_sync_function, arg1, arg2)
result = future.result()
```

### In Async Context

```python
from asgiref.sync import sync_to_async
from infras.executors import thread_pool

async def async_function():
    # Run sync function in thread pool
    result = await sync_to_async(sync_function, executor=thread_pool)(arg1, arg2)
    return result
```

### Custom Thread Pool

```python
from infras.executors import ThreadPoolManager

# Create custom thread pool manager
custom_manager = ThreadPoolManager(max_workers=10)
executor = custom_manager.executor

# Use the executor
future = executor.submit(heavy_computation)

# Shutdown when done
custom_manager.shutdown(wait=True)
```

### Application Shutdown

```python
from infras.executors import shutdown_thread_pool

# In your application shutdown handler
def shutdown_app():
    shutdown_thread_pool(wait=True)
```

## Configuration

The global thread pool is configured with:
- **Max workers**: 20 (optimized for database operations)
- **Thread prefix**: "db_adapter_worker"
- **Auto-shutdown**: No (manual shutdown required)

## Best Practices

1. **Use for I/O operations**: Thread pools are ideal for database operations, file I/O, and network calls
2. **Avoid CPU-intensive tasks**: For CPU-bound work, consider using `ProcessPoolExecutor`
3. **Proper shutdown**: Always shutdown thread pools when your application exits
4. **Monitor usage**: Use the logging to monitor thread pool usage and performance

## Performance Considerations

- **Connection pooling**: Thread pools work well with database connection pools
- **Async compatibility**: Designed to work seamlessly with async/await patterns
- **Resource management**: Proper cleanup prevents resource leaks 