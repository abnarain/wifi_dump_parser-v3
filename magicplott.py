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
        104.0:'|',
        6.0: '$6$',#CARETDOWN,
        60.0: '$60$',#'CARETRIGHT',
        40.5: '$40.5$',#'CARETLEFT',
        45.0:  '$45$', #CARETUP,
        135.0 : '$135$', #'TICKDOWN',
        270.0: '$270$',#'TICKUP',
        108.0: '$108$',#'TICKRIGHT',
        120.0: '$120$',#'TICKLEFT'
        }

color= [ 'blue', 'green', 'brown', 'red', 'purple', 'cyan', 'magenta', 'orange', 'yellow', 'pink',
        'lime', 'olive', 'chocolate','navy', 'teal', 'gray', 'black',  'darkred' , 'darkslategray',
        'violet', 'mediumvioletred' ,'orchid','tomato' , 'coral', 'goldenrod', 'tan', 'peru',  'sienna',
        'rosybrown','darkgoldenrod','navajowhite','darkkhaki','darkseagreen' ,'firebrick','lightst','crimson',
        ]

def plotter_scatter_rssi_rate(x_axis,y_axis,x_axis_label,y_axis_label,title,outfile_name):
    '''
    device id array
    dictionary of array of (rate,rssi)
    x label
    y label
    title
    output file name
    '''
    legend = []
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    _subplot = fig.add_subplot(1,1,1)
    index=0
    for k,v in y_axis.iteritems():
        print 'k is', k
        #rssi, rates
        print len(v[1]), len(v[0])
        if len(v[1])>0 and len(v[0])>0 :                
            _subplot.scatter(v[1],v[0],color=color[index],label=k)
            index=index+1
            
    _subplot.minorticks_on()
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05),scatterpoints=1)
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)
    _subplot.set_title(title)
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:        
        canvas.print_figure(outfile_name, dpi = 110)

def plotter_scatter(x_axis,y_axis,x_axis_label,y_axis_label,x_logscale,y_logscale,title,outfile_name):
    '''
    Input
    x_axis : a dictionary of list of lists {a:[[rate,retx],[]]}
    y_axis : a dictionary of contention delay
    x label
    y label
    bool for x logscale
    bool for y logscale
    title
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
#            print len(y_axis[key])
#            print "key is " , key
#            print "rates are ", rates_array
#            print "median is " , median(y_axis[key])
            if len(rates_array[val])==0 :
                break
            if val==0 :
                legend.append(key)
                lp=key
                lh.append(key)
            else:
                lp='_nolegend_'
            print rates_array[val][0]
            a = _subplot.scatter(rates_array[val][1], percentile(y_axis[key],90),s=50,color=color[index],marker=RATE_MARKERS[rates_array[val][0]],label=lp)
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
#    _subplot.set_xlim([0,1])
#    _subplot.set_ylim([0,20])
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:        
        canvas.print_figure(outfile_name, dpi = 110)



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
    #_subplot.set_ylim([0,100])
    _subplot.set_title(title)
    labels = _subplot.get_xticklabels()
    for label in labels:
        label.set_rotation(30)    
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)



def bar_graph_plotter(x_axis,y_axis ,x_axis_label, y_axis_label,title,outfile_name):
    legend = []
    ind = np.arange(len(x_axis))  # the x locations for the groups
    width = 0.35       # the width of the bars
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    _subplot = fig.add_subplot(1,1,1)
    rect1=_subplot.bar(ind,y_axis,color='b')
    #rect2=_subplot.bar(ind+width,y2_axis,color='g')
    #_subplot.legend((rect1[0]),('Device Counts'))
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05))
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)
    a= [i for i in range(0,len(x_axis))]
    _subplot.set_xticklabels(x_axis)
    _subplot.set_xticks(a)
    _subplot.set_title(title)
    labels = _subplot.get_xticklabels()
    for label in labels:
        label.set_rotation(30)
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)

def bar_graph_plotter_distr(x_axis_1,y_axis_1 ,x_axis_2, y_axis_2,x_axis_label, y_axis_label,title_1,title_2,outfile_name):
    legend = []
    ind = np.arange(len(x_axis_1))  # the x locations for the groups
    width = 0.35       # the width of the bars
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)
    _subplot = fig.add_subplot(2,1,1)
    rect1=_subplot.bar(ind,y_axis_1,width,color='r')
    _subplot.set_ylim([0,1])
    #rect2=_subplot.bar(ind+width,y2_axis,color='g')
    #_subplot.legend((rect1[0]),('bitrates'))
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05))
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)
    a= [i for i in range(0,len(x_axis_1))]
    _subplot.set_xticklabels(x_axis_1)
    _subplot.set_xticks(a)
    _subplot.set_title(title_1)
    labels = _subplot.get_xticklabels()
    for label in labels:
        label.set_rotation(30)
   
    ind = np.arange(len(x_axis_2))  # the x locations for the groups
    _subplot_2 = fig.add_subplot(2,1,2)
    rect2=_subplot_2.bar(ind,y_axis_2,width,color='b')
    #rect2=_subplot.bar(ind+width,y2_axis,color='g')
    #_subplot_2.legend((rect2[0]),('bitrates'))
    _subplot_2.set_ylim([0,1])
    _subplot_2.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05))   
    _subplot_2.set_ylabel(y_axis_label)                                      
    _subplot_2.set_xlabel(x_axis_label)                                      
    a= [i for i in range(0,len(x_axis_2))]                                   
    _subplot_2.set_xticklabels(x_axis_2)                                       
    _subplot_2.set_xticks(a)                                                  
    _subplot_2.set_title(title_2)
    labels = _subplot_2.get_xticklabels()
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)



def bar_graph_subplots(device_ids,x_axes,y_axes,x_axis_label, y_axis_label,title,outfile_name):
    legend = []
    width = 0.35       # the width of the bars
    fig = Figure(linewidth=0.0)
    fig.set_size_inches(fig_width,fig_length, forward=True)
    Figure.subplots_adjust(fig, left = fig_left, right = fig_right, bottom = fig_bottom, top = fig_top, hspace = fig_hspace)

    for i in range(0,len(device_ids)):
        print x_axes[i]
        ind = np.arange(len(x_axes[i]))  # the x locations for the groups
        _subplot = fig.add_subplot(len(device_ids),1,i)
        rect1=_subplot.bar(ind,y_axes[i],width,color=color[i])
        _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05))
        _subplot.set_ylabel(y_axis_label)
        _subplot.set_xlabel(x_axis_label)
        _subplot.set_xlim([0,10])
        d={0:'Video',
           1:'Voice',
           2:'Best Effort',
           3:'Background',
           8:'Multicast',
           }
        a=[]
        for j in range(0,len(x_axes[i])):
            a.append(d[x_axes[i][j]])
        _subplot.set_xticklabels(a)               
        #_subplot.set_xticks(a)        
        _subplot.set_title(title+ '('+device_ids[i]+')')
        labels = _subplot.get_xticklabels()
        for label in labels:
            label.set_rotation(30)  

    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)
