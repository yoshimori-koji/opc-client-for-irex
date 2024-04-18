import asyncio
import logging

from asyncua import Server
from generators import (
    consumed_power_generator,
    cycle_time_generator,
    error_generator,
    non_defective_generator,
    status_generator,
)

from models import Error, Status

END_POINT = "opc.tcp://localhost:4840/"
PARALLEL = 3

_logger = logging.getLogger(__name__)


async def main():
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint(END_POINT)

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)
    nodes = [await server.nodes.objects.add_object(idx, f"device{i:02}") for i in range(PARALLEL)]

    _logger.info("Starting server!")
    async with server:
        for i, node in enumerate(nodes):
            asyncio.create_task(send_power_variables(idx, node))
            asyncio.create_task(send_production_variables(idx, node))

        while True:
            await asyncio.sleep(1)


async def send_power_variables(idx, node, interval=1):
    _logger.info("init send_power_variables")

    # define generators
    status_gen = status_generator()
    consumed_power_gen = consumed_power_generator()
    error_gen = error_generator()

    # set initial value
    status = await anext(status_gen)
    error = await anext(error_gen)
    consumed_power = await anext(consumed_power_gen)

    # setup variables
    status_var = await node.add_variable(idx, "status", status.value)
    consumed_power_var = await node.add_variable(idx, "consumed_power", consumed_power)
    error_var = await node.add_variable(idx, "error", error.value)

    while True:
        status = await anext(status_gen) if error is Error.NOTHING else Status.ERROR
        error = await anext(error_gen) if status is Status.ERROR else Error.NOTHING
        consumed_power = await consumed_power_gen.asend(status)

        await asyncio.sleep(interval)

        await status_var.set_value(status.value)
        await consumed_power_var.set_value(consumed_power)
        await error_var.set_value(error.value)

        _logger.info("send power variables")


async def send_production_variables(idx, node):
    _logger.info("init send_production_variables")

    # define generators
    non_defectives_gen = non_defective_generator()
    cycle_time_gen = cycle_time_generator()
    consumption_supplies_gen = non_defective_generator()

    # set initial value
    production_volume = 0
    non_defectives = await anext(non_defectives_gen)
    cycle_time = await anext(cycle_time_gen)
    consumption_supplies = await anext(consumption_supplies_gen)

    # setup variables
    production_volume_var = await node.add_variable(idx, "production_volume", production_volume)
    non_defectives_var = await node.add_variable(idx, "non_defectives", non_defectives)
    cycle_time_var = await node.add_variable(idx, "cycle_time", cycle_time)
    consumption_supplies_var = await node.add_variable(
        idx, "consumption_suppliies", consumption_supplies
    )

    while True:
        production_volume += 1
        non_defectives = await anext(non_defectives_gen)
        cycle_time = await anext(cycle_time_gen)
        consumption_supplies = await anext(consumption_supplies_gen)

        await asyncio.sleep(cycle_time)

        await production_volume_var.set_value(production_volume)
        await non_defectives_var.set_value(non_defectives)
        await cycle_time_var.set_value(cycle_time)
        await consumption_supplies_var.set_value(consumption_supplies)

        _logger.info("send production variables")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(), debug=True)
