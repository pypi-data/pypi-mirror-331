import backtrader as bt
from ffquant.utils.Logger import Logger, stdout_log
import pytz
import requests
from ffquant.utils.Apollo import Apollo

class BaseStrategy(bt.Strategy):
    params = (
        ('name', None),
        ('logger', None),
        ('debug', None),
        ('test', None),
        ("check_chosen_strat", False)
    )

    def __init__(self):
        if self.p.logger is not None:
            self.logger = self.p.logger
        elif self.p.name is not None:
            self.logger = Logger(self.p.name)

        self.apollo = Apollo()
        if self.logger is not None and self.logger.name is not None:
            self.apollo = Apollo(namespace=self.logger.name)

    def next(self):
        cur_bar_date_str = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d")
        prev_bar_date_str = self.data.datetime.datetime(-1).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d")
        if prev_bar_date_str < cur_bar_date_str:
            stdout_log(f"re-initialize strategy due to date change from {prev_bar_date_str} to {cur_bar_date_str}")
            self.initialize()
            self.start()

    def initialize(self):
        pass

    def start(self):
        pass

    def get_perf_stats(self, port):
        result = None
        try:
            url = f"http://127.0.0.1:{port}/api/stats"
            return requests.get(url).json()
        except Exception as e:
            stdout_log(f"Failed to get performance stats. return None")
        return result