import random

from models import Status, Error


async def status_generator(weights=[1, 10, 1, 1], transition_rate=0.3):
    # population of transitions
    transitions = [True] * round(transition_rate * 100) + [False] * round(
        (1 - transition_rate) * 100
    )

    current = Status.STOP
    yield current

    while True:
        if random.choice(transitions):
            current = random.choices(
                [Status.STOP, Status.RUN, Status.ERROR, Status.SETUP], weights=weights
            )[0]
        yield current


async def error_generator(transition_rate=0.3):
    # population of transitions
    transitions = [True] * round(transition_rate * 100) + [False] * round(
        (1 - transition_rate) * 100
    )

    current = Error.NOTHING
    yield current

    while True:
        if current is Error.NOTHING:
            current = random.choice(
                [
                    Error.POWER,
                    Error.MECHANICAL,
                    Error.POWER_AND_MECHANICAL,
                    Error.OPERATION,
                    Error.POWER_AND_OPERATION,
                    Error.MECHANICAL_AND_OPERATION,
                    Error.ALL,
                ]
            )
        else:
            if random.choice(transitions):
                # turn off any one of the alarms
                v = current.value & random.choice(
                    [~Error.POWER.value, ~Error.MECHANICAL.value, ~Error.OPERATION.value]
                )
                current = Error(v)

        yield current


async def consumed_power_generator():
    current = 0
    status = Status.STOP

    while True:
        if status is Status.RUN or status is Status.ERROR:
            current += max(round(random.gauss(10, 5)), 1)

        status = yield current


async def non_defective_generator(rate=0.9):
    current = 0
    yield current
    while True:
        current += random.choices([0, 1], weights=[1 - rate, rate])[0]
        yield current


async def cycle_time_generator(mu=10, sigma=5):
    while True:
        yield round(max(random.gauss(mu, sigma), 1))


async def consumption_supplies_generator(rate=0.1):
    current = 0
    yield current
    while True:
        current += random.choices([0, 1], weights=[1 - rate, rate])[0]
        yield current
