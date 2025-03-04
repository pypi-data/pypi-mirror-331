import importlib
import logging
import os
from multiprocessing import Process, freeze_support, Queue, set_start_method, get_context
from sys import platform
from typing import List

from conductor.client.automator.task_runner import TaskRunner
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.metrics_settings import MetricsSettings
from conductor.client.telemetry.metrics_collector import MetricsCollector
from conductor.client.worker.worker import Worker
from conductor.client.worker.worker_interface import WorkerInterface

logger = logging.getLogger(
    Configuration.get_logging_formatted_name(
        __name__
    )
)

_decorated_functions = {}
_mp_fork_set = False
if not _mp_fork_set:
    try:
        if platform == 'win32':
            set_start_method('spawn')
        else:
            set_start_method('fork')
        _mp_fork_set = True
    except Exception as e:
        logger.info(f'error when setting multiprocessing.set_start_method - maybe the context is set {e.args}')
    if platform == "darwin":
        os.environ['no_proxy'] = '*'

def register_decorated_fn(name: str, poll_interval: int, domain: str, worker_id: str, func):
    logger.info(f'decorated {name}')
    _decorated_functions[(name, domain)] = {
        'func': func,
        'poll_interval': poll_interval,
        'domain': domain,
        'worker_id': worker_id
    }


class TaskHandler:
    def __init__(
            self,
            workers: List[WorkerInterface] = [],
            configuration: Configuration = None,
            metrics_settings: MetricsSettings = None,
            scan_for_annotated_workers: bool = True,
            import_modules: List[str] = None
    ):
        self.logger_process, self.queue = _setup_logging_queue(configuration)

        # imports
        importlib.import_module('conductor.client.http.models.task')
        importlib.import_module('conductor.client.worker.worker_task')
        if import_modules is not None:
            for module in import_modules:
                logger.info(f'loading module {module}')
                importlib.import_module(module)

        if workers is None:
            workers = []
        elif not isinstance(workers, list):
            workers = [workers]
        if scan_for_annotated_workers is True:
            for (task_def_name, domain) in _decorated_functions:
                record = _decorated_functions[(task_def_name, domain)]
                fn = record['func']
                worker_id = record['worker_id']
                poll_interval = record['poll_interval']

                worker = Worker(
                    task_definition_name=task_def_name,
                    execute_function=fn,
                    worker_id=worker_id,
                    domain=domain,
                    poll_interval=poll_interval)
                logger.info(f'created worker with name={task_def_name} and domain={domain}')
                workers.append(worker)

        self.__create_task_runner_processes(workers, configuration, metrics_settings)
        self.__create_metrics_provider_process(metrics_settings)
        logger.info('TaskHandler initialized')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_processes()

    def stop_processes(self) -> None:
        self.__stop_task_runner_processes()
        self.__stop_metrics_provider_process()
        logger.info('Stopped worker processes...')
        self.queue.put(None)
        self.logger_process.terminate()

    def start_processes(self) -> None:
        logger.info('Starting worker processes...')
        freeze_support()
        self.__start_task_runner_processes()
        self.__start_metrics_provider_process()
        logger.info('Started all processes')

    def join_processes(self) -> None:
        try:
            self.__join_task_runner_processes()
            self.__join_metrics_provider_process()
            logger.info('Joined all processes')
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt: Stopping all processes')
            self.stop_processes()

    def __create_metrics_provider_process(self, metrics_settings: MetricsSettings) -> None:
        if metrics_settings is None:
            self.metrics_provider_process = None
            return
        self.metrics_provider_process = Process(
            target=MetricsCollector.provide_metrics,
            args=(metrics_settings,)
        )
        logger.info('Created MetricsProvider process')

    def __create_task_runner_processes(
            self,
            workers: List[WorkerInterface],
            configuration: Configuration,
            metrics_settings: MetricsSettings
    ) -> None:
        self.task_runner_processes = []
        for worker in workers:
            self.__create_task_runner_process(
                worker, configuration, metrics_settings
            )

    def __create_task_runner_process(
            self,
            worker: WorkerInterface,
            configuration: Configuration,
            metrics_settings: MetricsSettings
    ) -> None:
        task_runner = TaskRunner(worker, configuration, metrics_settings)
        process = Process(target=task_runner.run)
        self.task_runner_processes.append(process)

    def __start_metrics_provider_process(self):
        if self.metrics_provider_process is None:
            return
        self.metrics_provider_process.start()
        logger.info('Started MetricsProvider process')

    def __start_task_runner_processes(self):
        n = 0
        for task_runner_process in self.task_runner_processes:
            task_runner_process.start()
            n = n + 1
        logger.info(f'Started {n} TaskRunner process')

    def __join_metrics_provider_process(self):
        if self.metrics_provider_process is None:
            return
        self.metrics_provider_process.join()
        logger.info('Joined MetricsProvider processes')

    def __join_task_runner_processes(self):
        for task_runner_process in self.task_runner_processes:
            task_runner_process.join()
        logger.info('Joined TaskRunner processes')

    def __stop_metrics_provider_process(self):
        self.__stop_process(self.metrics_provider_process)

    def __stop_task_runner_processes(self):
        for task_runner_process in self.task_runner_processes:
            self.__stop_process(task_runner_process)

    def __stop_process(self, process: Process):
        if process is None:
            return
        try:
            logger.debug(f'Terminating process: {process.pid}')
            process.terminate()
        except Exception as e:
            logger.debug(f'Failed to terminate process: {process.pid}, reason: {e}')
            process.kill()
            logger.debug(f'Killed process: {process.pid}')


# Setup centralized logging queue
def _setup_logging_queue(configuration: Configuration):
    queue = Queue()
    if configuration:
        configuration.apply_logging_config()
        log_level = configuration.log_level
        logger_format = configuration.logger_format
    else:
        log_level = logging.DEBUG
        logger_format = None

    logger.setLevel(log_level)

    # start the logger process
    logger_p = Process(target=__logger_process, args=(queue, log_level, logger_format))
    logger_p.start()
    return logger_p, queue


# This process performs the centralized logging
def __logger_process(queue, log_level, logger_format=None):
    c_logger = logging.getLogger(
        Configuration.get_logging_formatted_name(
            __name__
        )
    )

    c_logger.setLevel(log_level)

    # configure a stream handler
    sh = logging.StreamHandler()
    if logger_format:
        formatter = logging.Formatter(logger_format)
        sh.setFormatter(formatter)
    c_logger.addHandler(sh)

    # run forever
    while True:
        # consume a log message, block until one arrives
        message = queue.get()
        # check for shutdown
        if message is None:
            break
        # log the message
        c_logger.handle(message)
