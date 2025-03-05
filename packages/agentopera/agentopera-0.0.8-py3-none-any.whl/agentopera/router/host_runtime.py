import asyncio
import platform
from agentopera.agents.runtimes.grpc import GrpcWorkerAgentRuntimeHost

from agentopera.utils.logger import logger

async def run_host():
    # Initialize host runtime
    host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
    host.start()  # Start the host in the background

    # Handle shutdown gracefully
    if platform.system() == "Windows":
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await host.stop()
    else:
        await host.stop_when_signal()

if __name__ == "__main__":
    logger.info("start to run host runtime")
    asyncio.run(run_host())