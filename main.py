import threading
import signal
import sys

from flask_app import run_flask_app
from aiogram_app import run_aiogram_app, on_bot_shutdown
import asyncio


def main():
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    loop = asyncio.get_event_loop()

    def shutdown_handler(sig, frame):
        print("\n🔻 Received shutdown signal. Cleaning up...")
        loop.create_task(on_bot_shutdown())
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    run_aiogram_app()


if __name__ == "__main__":
    main()
