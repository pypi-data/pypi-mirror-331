from typing import List, Callable, AsyncGenerator
import asyncio

class EventCollector:
    """
    支持运行时的事件收集
    """
    def __init__(self):
        self.event_sources: List[Callable[[], AsyncGenerator]] = []
        self.queue = asyncio.Queue()

    def add_event_source(self, event_source: Callable[[], AsyncGenerator]):
        """添加一个事件源，该事件源应该是一个异步生成器"""
        self.event_sources.append(event_source)
    
    async def producer(self, gen: AsyncGenerator):
        async for item in gen:  # 异步生成器
            await self.queue.put(item)
        await self.queue.put(None)  # 自动的停止标志

    async def consumer(self, max_producers):
        count = 0  # source完成的标志
        while True:
            item = await self.queue.get()
            if item is None:
                count += 1
                if count == max_producers:
                    break
            else:
                yield item
            self.queue.task_done()

    async def all_events_generator(self):
        """返回流式所有的事件源信息，事件源停止后，不再返回事件"""
        producers = [
            asyncio.create_task(self.producer(gen()))
            for gen in self.event_sources
        ]
        consumer = self.consumer(len(producers))
        
        return consumer
    
        # 等待所有的生产者结束
        await asyncio.gather(*producers)


class FakeEventSource_3():

    def __init__(self) -> None:
        self.fe3_msg = "in1"

    async def run_chat(self, evc: EventCollector):
        msg = ""
        msg += self.fe3_msg
        for i in range(3):
            round = i + 1
            gen = self.gen_reply(msg, round)
            evc.add_event_source(lambda: gen)
            await asyncio.sleep(0)  # 允许事件循环处理其他任务

    async def gen_reply(self, msg, round: int) -> AsyncGenerator:
        outputs = [f'{msg}-r{round}-c1', f'{msg}-r{round}-c2']
        full_response = ""
        for i, x in enumerate(outputs):
            await asyncio.sleep(1)  # 模拟异步操作
            full_response += x
            self.fe3_msg = x
            yield {
                "data": x,
                "event": f"fe3.round{round}.chunk{i}",
            }
        msg += full_response

async def main():
    evc = EventCollector()
    fake_event_source = FakeEventSource_3()
    await fake_event_source.run_chat(evc)

    evg = await evc.all_events_generator()
    async for event in evg:
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
