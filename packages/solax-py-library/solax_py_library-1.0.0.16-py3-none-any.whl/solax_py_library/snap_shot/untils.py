from .exceptions import SnapshotTimeoutError
import asyncio


def retry(max_attempts=3, delay=0.5):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"尝试 {attempts+1} 失败: {e}")
                    await asyncio.sleep(delay)
                    attempts += 1
            raise SnapshotTimeoutError(f"操作失败 {max_attempts} 次")

        return wrapper

    return decorator
