import simpy
from dataclasses import dataclass
import random


@dataclass
class Robot:
    env: simpy.Environment

    id: int
    watt: int = 0  # 電力量（初日からの累積値） 単位：kwh
    product_num: int = 0  # 生産数（初日からの累積数） 単位:個
    accept_num: int = 0  # 良品数（初日からの累積数） 単位:個
    used_num: int = 0  # 消耗品交換後の累積値 単位:個
    status: int = 0  # 通常停止中=0, 運転中=1, 異常停止中=2, 段取り中=3
    errcode: int = 0  # 電源系アラームが1bit目、機械系アラームが2bit目、操作系アラームが3bit目

    @property
    def cycle_time(self):
        # １ワークあたりのサイクルタイム(100ミリ秒)
        return max(random.gauss(mu=100, sigma=30), 1)

    def product(self, cycle_time_sec):
        self.product_num += 1

        quality = random.gauss(mu=0.9, sigma=0.1)
        self.accept_num += random.choices([1, 0], [quality, 1 - quality])[0]

        used_rate = random.gauss(mu=0.1, sigma=0.04)
        self.used_num += random.choices([1, 0], [used_rate, 1 - used_rate])[0]

        self.watt += cycle_time_sec * random.gauss(5, 1)

    def change_status(self):
        self.status = random.choices([0, 1, 2, 3], [0.03, 0.9, 0.03, 0.03])[0]
        if self.status == 1:
            self.errcode = 0
        else:
            self.errcode = random.randint(1, 7)


def change_status(env):
    model = env.model
    work_event = None

    while True:
        model.change_status()

        if model.status == 1:
            work_event = env.process(work(env))
        elif work_event is not None and work_event.is_alive:
            work_event.interrupt()

        print(f"Change Status {model.status} {env.now}")

        yield env.timeout(random.gauss(10 * 60, 1 * 60))


def work(env):
    try:
        model = env.model
        while True:
            cycle_time = model.cycle_time
            cycle_time_sec = cycle_time / 10

            yield env.timeout(cycle_time_sec)

            model.product(cycle_time_sec)

            print(f"Producted {model.product_num} {env.now}")

    except simpy.Interrupt:
        print(f"Interrupted {env.now}")


# シミュレーションプロセスを開始
# env = simpy.RealtimeEnvironment()
env = simpy.Environment()
env.model = Robot(env, 1)
env.process(change_status(env))

# シミュレーションを実行
env.run(until=3600)  # 1時間分のシミュレーション（60分）
