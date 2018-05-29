import asyncio
import unittest


class FakedObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class FakedObjectTest(unittest.TestCase):
    def test_context_manager(self):
        name = 'jack'
        age = 21
        with FakedObject(name=name, age=age) as obj:
            self.assertEqual(name, obj.name)
            self.assertEqual(age, obj.age)

    def test_async_context_manager(self):
        name = 'Mary'
        age = 19

        async def work():
            async with FakedObject(name=name, age=age) as obj:
                self.assertEqual(name, obj.name)
                self.assertEqual(age, obj.age)
                await asyncio.sleep(0.1)

        asyncio.get_event_loop().run_until_complete(work())


if __name__ == '__main__':
    unittest.main()
