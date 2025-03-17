import asyncio
import redis.asyncio as redis

async def init_redis():
    redis_client = await redis.Redis(host='localhost', port=6379, decode_responses=True)
    return redis_client

async def set_key(redis_client):
    await redis_client.set('name', 'John')

async def get_key(redis_client):
    value = await redis_client.get('name')
    print(f"Name: {value}")

async def main():
    redis_client = await init_redis()  # Initialize Redis client
    await set_key(redis_client)
    
asyncio.run(main()) 