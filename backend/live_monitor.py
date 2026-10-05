import asyncio
import os


async def watch_log_file(file_path):
    """
    Watch a log file and yield new lines
    whenever they are added.
    """

    position = os.path.getsize(
        file_path
    )

    while True:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            file.seek(position)

            lines = file.readlines()

            position = file.tell()

        for line in lines:
            if line.strip():
                yield line.strip()

        await asyncio.sleep(0.5)