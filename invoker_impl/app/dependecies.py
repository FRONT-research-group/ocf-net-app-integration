import asyncio

task_registry: dict[str,asyncio.Task] = {}



def get_task_registry() -> dict[str, asyncio.Task]:
        """
        Returns the current task registry.

        Returns:
            dict[str, asyncio.Task]: A dictionary mapping task IDs to asyncio Task objects.
        """
        return task_registry