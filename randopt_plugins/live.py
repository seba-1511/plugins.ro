#!/usr/bin/env python3

from matplotlib import pyplot as plt
from terminaltables import SingleTable


class Live(object):

    def __init__(self, experiment, metrics=[], live_plot=True, live_table=False):
        self.live_plot = live_plot
        self.live_table = live_table
        self.experiment = experiment
        self.metrics = {m: [] for m in metrics}

    def __getattr__(self, attr):
        if attr in self.metrics.keys():
            return self.metrics[attr][-1]
        return getattr(self.experiment, attr)

    def update(self, key, value=None):
        if value is None:
            assert(isinstance(key, dict))
            for k in key.keys():
                self.update(k, value=key[k])
        else:
            assert(key in self.metrics.keys())
            self.metrics[key].append(value)
        if self.live_plot:
            self.plot_metrics()

    def table_metrics(self):
        # Returns a printable table of metrics
        data = [[m, self.metrics[m][-1]] for m in self.metrics.keys()]
        table = SingleTable(data, self.experiment.name)
        table.inner_heading_row_border = True
        table.inner_row_border = True
        table.inner_column_border = True
        return table.table

    def plot_metrics(self):
        # Updates live visualizations for all metrics
        pass

    def add_result(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data'].update(self.metrics)
        elif len(args) > 1 and isinstance(args[1], dict):
            args[1].update(self.metrics)
        else:
            kwargs['data'] = self.metrics
        self.experiment.add_result(*args, **kwargs)
