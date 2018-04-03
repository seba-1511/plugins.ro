#!/usr/bin/env python3

import os
import sys
import subprocess
import signal
import math
import time
import numpy as np
import visdom
import logging
import webbrowser
from visdom.server import download_scripts, main
from multiprocessing import Process
from terminaltables import SingleTable

def kill_child_processes(signum, frame):
    parent_id = os.getpid()
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_id, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    retcode = ps_command.wait()
    for pid_str in ps_output.strip().split("\n")[:-1]:
        os.kill(int(pid_str), signal.SIGTERM)
    sys.exit()


class Vislive(object):

    def __init__(self, experiment, metrics=[], live_plot=False):
        self.live_plot = live_plot
        self.experiment = experiment
        self.metrics = {m: [] for m in metrics}
        self.subplots = None
        self.visdom_server = None

    def __getattr__(self, attr):
        if attr in self.metrics.keys():
            return self.metrics[attr][-1]
        return getattr(self.experiment, attr)

    def update(self, key, value=None, update_plots=True):
        if value is None:
            assert(isinstance(key, dict))
            for k in key.keys():
                self.update(k, value=key[k], update_plots=False)
        else:
            assert(key in self.metrics.keys())
            self.metrics[key].append(value)
        if self.live_plot and update_plots:
            self.plot_metrics()

    def table_metrics(self):
        # Returns a printable table of metrics
        data = [[m, self.metrics[m][-1]] for m in self.metrics.keys()]
        table = SingleTable(data, self.experiment.name)
        table.inner_heading_row_border = True
        table.inner_row_border = True
        table.inner_column_border = True
        return table.table

    def _start_visdom_server(self):
        def server():
            sys.stdout = open(os.devnull, "w")
            logging.getLogger().setLevel('WARN')
            main()
        download_scripts()
        self.visdom_server = Process(target=server)
        self.visdom_server.start()
        signal.signal(signal.SIGTERM, kill_child_processes)
        time.sleep(1.0)
        webbrowser.open('http://localhost:8097')
        print('Visdom was started on port 8097.')


    def _create_subplots(self):
        vis = visdom.Visdom()
        if not vis.check_connection():
            self._start_visdom_server()
        self.visdom = vis
        self.subplots = [vis.line(X=np.zeros(1),
                                  Y=np.zeros(1),
                                  opts={'title': self.name + ' - ' + m})
                         for m in self.metrics.keys()]

    def plot_metrics(self):
        # Updates live visualizations for all metrics
        if self.subplots is None:
            self._create_subplots()
        for m, sbp in zip(self.metrics.keys(), self.subplots):
            self.visdom.line(X=np.arange(len(self.metrics[m])),
                             Y=np.array(self.metrics[m]),
                             win=sbp,
                             update='replace')


    def add_result(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data'].update(self.metrics)
        elif len(args) > 1 and isinstance(args[1], dict):
            args[1].update(self.metrics)
        else:
            kwargs['data'] = self.metrics
        self.experiment.add_result(*args, **kwargs)

    def close(self):
        if self.visdom_server is not None:
            self.visdom_server.terminate()
