#!/usr/bin/env python3

import randopt as ro
from randopt_plugins.vislive import Vislive
from time import sleep, time

if __name__ == '__main__':
    exp = ro.Experiment('live_example', params={
        'x': ro.Gaussian(),
        'y': ro.Gaussian()
    })
    live = Vislive(exp, metrics=['square', 'norm', 'xminusy', 'time'])
    live.update({
        'square': 0.0,
        'norm': 0.0,
        'xminusy': 0.0,
        'time': 0.0
    })

    start = time()
    for i in range(10):
        live.sample_all_params()
        live.update('square', live.x**2)
        live.update({
            'norm': abs(exp.y),
            'xminusy': exp.x - exp.y,
            'time': time() - start
        })
        print(live.table_metrics())
        live.plot_metrics()
        sleep(1)

    live.add_result(exp.x - exp.y)
    live.add_result(exp.x - exp.y, {'useless': [0, 0, 0, 0]})
    live.add_result(exp.x - exp.y, data={'useless': [0, 0, 0, 0]})
    live.close()
