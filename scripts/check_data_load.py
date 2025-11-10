# Quick check script to verify data loading after changing config
from klinechart import config
from klinechart.data_loader import load_data
import itertools

conf = config.conf
print("Loaded config plots count:", len(conf.get('plots', [])))

datas = load_data(conf)
print("Loaded datas plots:", list(datas.keys()))

# inspect first plot/item
first_plot = next(iter(datas.values()))
first_item = next(iter(first_plot.values()))

bars = getattr(first_item, 'bars', None)
if bars is None:
    print('No bars found on the first chart item')
else:
    print('bars_count:', len(bars))
    print('\nFirst 5 bars:')
    for i, b in enumerate(list(bars.values())[:5]):
        print(i, b)
