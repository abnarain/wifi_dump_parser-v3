import sys, os, numpy, math, time
import matplotlib.font_manager
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import datetime as dt
from utils import *
try:
    import cPickle as pickle
except ImportError:
    import pickle
LEGEND_PROP = matplotlib.font_manager.FontProperties(size=6)
# Figure dimensions                                                                                                   
fig_width = 12
fig_length = 12.25
# Can be used to adjust the border and spacing of the figure    
fig_left = 0.12
fig_right = 0.94
fig_bottom = 0.25
fig_top = 0.94
fig_hspace = 0.5
row=1
column=1
RATE_MARKERS = {
        1.0 :'+',2.0: 'x',5.5:'s',6.5:'o',11.0:'^',
        13.0:'H',18.0:'>',19.5:'h',26.0:'v',36.0:'p',
        39.0:'<',48.0:'*',54.0:'D',52.0:'1',58.5:'2',
        65.0:'3',78.0:'4',117.0 :'8',130.0:'_',
        104.0:'|',6.0:'CARETDOWN',45.0:'CARETUP',60.0:'CARETRIGHT',40.5:'CARETLEFT',
        135:'TICKDOWN', 270.0:'TICKUP',108.0:'TICKRIGHT',120.0:'TICKLEFT'
        }

color= ['black', 'blue', 'green', 'brown', 'red', 'purple', 'cyan', 'magenta', 'orange', 'yellow', 'pink',
        'lime', 'olive', 'chocolate','navy', 'teal', 'gray', 'crimson',  'darkred' , 'darkslategray',
        'violet', 'mediumvioletred' ,'orchid','tomato' , 'coral', 'goldenrod', 'tan', 'peru',  'sienna',
        'rosybrown','darkgoldenrod','navajowhite','darkkhaki','darkseagreen' ,'firebrick','lightst'
        ]

def plotter_scatter(x_axis,y_axis,x_axis_label,y_axis_label,x_logscale,y_logscale,title,outfile_name):
    '''
    Input
    x_axis : a dictionary of list of lists {a:[[rate,retx],[]]}
    y_axis : a dictionary of contention delay
    x label
    y label
    Outputs a plot
    '''
    legend = []
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    #sorted(homes_percentile.items(), key=lambda x: x[1])
    index=0
    rates_encountered=[]
    li=[]
    lh=[]
    _subplot = fig.add_subplot(1,1,1)
    for key,rates_array in x_axis.iteritems():
        for val in range(0,len(rates_array)) :
            lp=None
            if len(rates_array[val])==0 :
                break
            if val==0 :
                legend.append(key)
                lp=key
                lh.append(key)
            else:
                lp='_nolegend_'
            print rates_array[val][0]
            a = _subplot.scatter(rates_array[val][1],median(y_axis[key]),s=50,color=color[index],marker=RATE_MARKERS[rates_array[val][0]],label=lp)
            #_subplot.boxplot(contention_table[key]),positions=rates_array[val][1])
            if rates_array[val][0] in rates_encountered:
                pass
            else:
                rates_encountered.append(rates_array[val][0])
                li.append(a)
        index = index+1
    legend2=_subplot.legend(li,RATE_MARKERS,bbox_to_anchor=(0.9,-0.05), prop=LEGEND_PROP,loc=2)
    _subplot.add_artist(legend2)
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05),scatterpoints=1)
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)
    _subplot.set_title(title)
    if x_logscale :
        _subplot.set_xscale('log')
    if y_logscale :
        _subplot.set_yscale('log')
    _subplot.set_xlim([0,1])
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)


def plotter_boxplot(x_axis,y_axis, x_axis_label, y_axis_label,title,outfile_name):
    legend = []
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    _subplot = fig.add_subplot(1,1,1)
    _subplot.boxplot(y_axis,notch=0, sym='+', vert=1, whis=1.5)
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05))
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)
    a= [i for i in range(0,len(x_axis))]
    _subplot.set_xticklabels(x_axis)
    _subplot.set_xticks(a)
    _subplot.set_ylim([0,100])
    _subplot.set_title(title)
    labels = _subplot.get_xticklabels()
    for label in labels:
        label.set_rotation(30)

    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)

