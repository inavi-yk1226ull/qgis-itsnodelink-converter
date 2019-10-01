from qgis.core import QgsTask, QgsTaskManager
from time import sleep

import random


def run1(task, time):
    wait_time = time / 100.0
    sum = 0
    iterations = 0
    for i in range(101):
        sleep(wait_time)
        print(i)
        task.setProgress(i)
        sum += random.randint(0, 100)
        iterations += 1
        if task.isCanceled():
            return
    task.result = [sum, iterations]


def CheckDbData():
    task = QgsTask.fromFunction('waste cpu', run1, 2)
    mgr = QgsTaskManager()
    mgr.addTask(task)
    task.isFinished()
    pass
