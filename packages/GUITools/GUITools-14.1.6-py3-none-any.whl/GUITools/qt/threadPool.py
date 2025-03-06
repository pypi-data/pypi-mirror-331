# coding: utf-8

import queue
import asyncio
from typing import Callable
from PyQt6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    pyqtSignal,
    pyqtSlot,
    QTimer,
)

class WorkerSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()

class Worker(QRunnable):
    def __init__(self, func, *arg):
        super().__init__()
        self.func = func
        self.arg = arg
        self.signals = WorkerSignals()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if asyncio.iscoroutinefunction(self.func):
                result = loop.run_until_complete(self.func(self.arg[0])) if self.arg else  loop.run_until_complete(self.func())
            else:
                result = self.func(self.arg[0]) if self.arg else self.func()
        except Exception as e:
            result = f"Erro: {str(e)}"
        finally:
            loop.close()

        self.signals.result.emit(result)
        self.signals.finished.emit()

class Processing(QObject):
    target_callback_signal = pyqtSignal(object)
    def __init__(self, target: Callable, update_func: Callable = None, callback: Callable = None, interval: int = 1, global_instance: bool = False, wait : bool=False, initialize : bool=True):
          super().__init__()
          self.target = target
          self.update_func = update_func
          self.callback = callback
          self.interval = interval * 1000  

          if global_instance:
               self.threadpool = QThreadPool.globalInstance()
          else:
               self.threadpool = QThreadPool()

          if callback:
               self.target_callback_signal.connect(self.callback)

          if initialize:
               self.start()
               if wait:
                    self.threadpool.waitForDone()
                    
          if self.update_func and not wait:
               self.timer = QTimer()
               self.timer.timeout.connect(self.update_func)
               self.timer.start(self.interval)

    def start(self):
        worker = Worker(self.target)
        worker.signals.result.connect(self.handle_result)
        self.threadpool.start(worker)

    @pyqtSlot(object)
    def handle_result(self, result):
        self.target_callback_signal.emit(result)

class Multiprocessing(QObject):
    final_signal = pyqtSignal()
    target_callback_signal = pyqtSignal(object)

    def __init__(self, args : list, target : Callable, target_callback : Callable = None, final_callback : Callable = None, max_threads : int=5, global_instance : bool = False, wait : bool=False, initialize : bool=True):
        super().__init__()
        self.target = target
        self.final_callback = final_callback
        self.target_callback = target_callback
        self.max_threads = max_threads

        self.my_queue = queue.Queue()
        for arg in args:
            self.my_queue.put(arg)

        if global_instance:
            self.threadpool = QThreadPool.globalInstance()
        else:
            self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(max_threads)

        self.active_threads = 0

        if final_callback:
            self.final_signal.connect(self.final_callback)
        if target_callback:
            self.target_callback_signal.connect(self.target_callback)

        if initialize:
            self.start()
            if wait:
                self.threadpool.waitForDone()

    def start(self):
        for _ in range(min(self.max_threads, self.my_queue.qsize())):
            self._start_next_task()

    def _start_next_task(self):
        if not self.my_queue.empty():
            arg = self.my_queue.get()
            worker = Worker(self.target, arg)

            worker.signals.result.connect(self.handle_result)
            worker.signals.finished.connect(self.handle_finished)

            self.active_threads += 1
            self.threadpool.start(worker)

    @pyqtSlot(object)
    def handle_result(self, result):
        self.target_callback_signal.emit(result)

    @pyqtSlot()
    def handle_finished(self):
        self.active_threads -= 1
        if not self.my_queue.empty():
            self._start_next_task()
        elif self.active_threads == 0:
            self.final_signal.emit()