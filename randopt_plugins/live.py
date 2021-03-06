#!/usr/bin/env python3

import math
import time
import numpy as np
from matplotlib import pyplot as plt
from terminaltables import SingleTable


class Live(object):

    def __init__(self, experiment, metrics=[], live_plot=False):
        self.live_plot = live_plot
        self.experiment = experiment
        self.metrics = {m: [] for m in metrics}
        self.subplots = None

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

    def _create_subplots(self):
        num_plots = len(self.metrics.keys())
        grid_size = int(math.ceil(math.sqrt(num_plots))) 
        grid_prefix = 110 * grid_size
        self.subplots = []
        self.lines = []
        plt.ion()
        plt.suptitle(self.experiment.name + ' Live Metrics')
        for i, m_key in enumerate(self.metrics.keys()):
            sbp = plt.subplot(grid_prefix + i + 1)
            self.subplots.append(sbp)
            line, = sbp.plot([], [], label=m_key)
            sbp.legend()
            self.lines.append(line)

    def plot_metrics(self):
        # Updates live visualizations for all metrics
        # TODO: Plotting is quite slow. (0.1s/metric)
        if self.subplots is None:
            self._create_subplots()

#        for sbp, m_key in zip(self.subplots, self.metrics.keys()):
        for sbp, line, m_key in zip(self.subplots, self.lines, self.metrics.keys()):
            y = self.metrics[m_key]
            x = list(range(len(y)))
            line.set_data(np.array(x), np.array(y))
            sbp.set_xlim(0, len(x))
            sbp.set_ylim(min(y) - 0.1 * abs(min(y)),
                         max(y) + 0.1 * abs(max(y)))

        # This renders the figure
        plt.draw()
        plt.pause(1.5)

    def add_result(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data'].update(self.metrics)
        elif len(args) > 1 and isinstance(args[1], dict):
            args[1].update(self.metrics)
        else:
            kwargs['data'] = self.metrics
        self.experiment.add_result(*args, **kwargs)
