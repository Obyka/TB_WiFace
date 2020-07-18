# this code comes from: https://gist.github.com/bbengfort/0938048f364a8c0d6ae3#file-timeline-py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from operator import itemgetter
from collections import defaultdict


def plot_timeline(dataset, **kwargs):
    """
    Plots a timeline of events from different sources to visualize a relative
    sequence or density of events. Expects data in the form of:
        (timestamp, source, category)
    Though this can be easily modified if needed. Expects sorted input.
    """
    outpath = kwargs.pop('savefig', None)  # Save the figure as an SVG
    colors  = kwargs.pop('colors', {})     # Plot the colors for the series.
    series  = set([])                      # Figure out the unique series

    # Bring the data into memory and sort
    dataset = sorted(list(dataset), key=itemgetter(0))

    # Make a first pass over the data to determine number of series, etc.
    for _, source, category in dataset:
        series.add(source)
        if category not in colors:
            colors[category] = 'k'

    # Sort and index the series
    series  = sorted(list(series))

    # Create the visualization
    x = []  # Scatterplot X values
    y = []  # Scatterplot Y Values
    c = []  # Scatterplot color values

    # Loop over the data a second time
    for timestamp, source, category in dataset:
        x.append(timestamp)
        y.append(series.index(source))
        c.append(colors[category])

    probe_patch = mpatches.Patch(color='green', label='Probe request')
    pricture_patch = mpatches.Patch(color='blue', label='Picture taken')
    arrival_patch = mpatches.Patch(color='red', label='Arrival and departure')


    plt.figure(figsize=(14,4))
    plt.title(kwargs.get('title', "Timeline Plot"))
    plt.xlabel('Time in seconds')
    plt.ylabel('Identities UUID')
    plt.ylim((-1,len(series)))
    plt.xlim((0, dataset[-1][0]+1000))
    plt.yticks(range(len(series)), series)
    plt.scatter(x, y, color=c, alpha=0.85, s=10)
    plt.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1), handles=[probe_patch, pricture_patch, arrival_patch])
    plt.subplots_adjust(bottom=.25, left=.25)

    if outpath:
        plt.tight_layout()
        return plt.savefig(outpath, format='svg', dpi=1200)

    return plt