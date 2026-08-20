import asyncio
from collections import defaultdict


class SSEManager:
    def __init__(self) -> None:
        self._subscribers: dict[
            int,
            set[asyncio.Queue[dict]],
        ] = defaultdict(set)

        self._lock = asyncio.Lock()

    async def subscribe(
        self,
        generation_id: int,
    ) -> asyncio.Queue[dict]:
        queue: asyncio.Queue[dict] = asyncio.Queue()

        async with self._lock:
            self._subscribers[generation_id].add(queue)

        return queue

    async def unsubscribe(
        self,
        generation_id: int,
        queue: asyncio.Queue[dict],
    ) -> None:
        async with self._lock:
            subscribers = self._subscribers.get(generation_id)

            if subscribers is None:
                return

            subscribers.discard(queue)

            if not subscribers:
                del self._subscribers[generation_id]

    async def publish(
        self,
        generation_id: int,
        event: dict,
    ) -> None:
        async with self._lock:
            subscribers = list(
                self._subscribers.get(generation_id, set())
            )

        for queue in subscribers:
            await queue.put(event)


sse_manager = SSEManager()