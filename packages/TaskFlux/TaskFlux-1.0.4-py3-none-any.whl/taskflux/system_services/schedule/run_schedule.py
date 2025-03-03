# -*- encoding: utf-8 -*-

import sys
import time
import argparse

from taskflux.ameta.key import *
from taskflux.logger import *
from taskflux.utils import *
from taskflux.queue import *


class RunSchedule:
    """
    Singleton class for managing the run schedule.
    """

    def __init__(self, config):
        """
        Initializes the RunSchedule instance.
        Args:
            config (dict): The configuration dictionary.
        """
        initialization_logger(config=config)
        initialization_rabbitmq(config=config)

        self.config = config
        self.system_default_schedule_time = config.get(KEY_DEFAULT_SCHEDULE_TIME, 10)
        self.logger = logger(filename=KEY_PROJECT_NAME, task_id='task_distribution')

    def task_distribution(self):
        """
        Distributes tasks based on the configuration.
        """
        send_message(
            queue='{}_task_distribution'.format(KEY_SYSTEM_SERVICE_NAME),
            message={
                'self_config': self.config,
                KEY_TASK_ID: 'task_distribution',
                KEY_TASK_IS_SUB_TASK: False
            }
        )

    def run(self):
        while True:
            try:
                self.task_distribution()
                time.sleep(self.system_default_schedule_time)
            except Exception as e:
                self.logger.error('run schedule error: {}'.format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run schedule script")

    parser.add_argument("--config", type=str, help="run schedule config")
    args = parser.parse_args()

    configs = load_config(args.config)

    sys.path.append(configs[KEY_ROOT_PATH])

    RunSchedule(config=configs).run()
