import asyncio
import aiohttp
import time
import argparse
from itertools import count

async def call(url, session, request_num, start_time, enable_timing):
    """Send a single request and log status with optional timing."""
    try:
        async with session.get(url) as response:
            if enable_timing:
                elapsed = time.time() - start_time
                print(f"[{elapsed:.2f}s] Request #{request_num} returned status {response.status}")
            else:
                print(f"Request #{request_num} returned status {response.status}")
    except Exception as e:
        print(f"Request #{request_num} failed: {e}")

async def send_requests(url, total_requests, concurrency, enable_timing):
    """Manages batch sending of requests with controlled concurrency."""
    start_time = time.time()
    request_counter = count(1)  # Infinite iterator for request numbering
    semaphore = asyncio.Semaphore(concurrency)

    # Use a single session across all requests for efficiency
    async with aiohttp.ClientSession() as session:
        # Dispatch tasks in controlled batches
        tasks = [
            call(url, session, next(request_counter), start_time, enable_timing)
            for _ in range(total_requests)
        ]
        # Run tasks with concurrency control
        for i in range(0, len(tasks), concurrency):
            await asyncio.gather(*tasks[i:i + concurrency])

    print("All requests sent.")

def main():
    # Parse command-line arguments for flexibility and control
    parser = argparse.ArgumentParser(description="High-performance request sender with concurrency control and timing.")
    parser.add_argument("url", type=str, help="The target URL to send requests to (include http:// or https://).")
    parser.add_argument("requests", type=int, help="Total number of requests to send.")
    parser.add_argument("-c", "--concurrency", type=int, default=100, help="Number of concurrent requests.")
    parser.add_argument("-t", "--timing", action="store_true", help="Enable timing log for each request.")
    args = parser.parse_args()

    # Run the main request function with the provided settings
    asyncio.run(send_requests(args.url, args.requests, args.concurrency, args.timing))

if __name__ == "__main__":
    main()
