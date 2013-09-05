#Author : Abhinav Narain
#Date : 5-sept-2013
#Purpose : To plot the devices inside homes 
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

color= ['black', 'blue', 'green', 'brown', 'red', 'purple', 'cyan', 'magenta', 'orange', 'yellow', 'pink', 
        'lime', 'olive', 'chocolate','navy', 'teal', 'gray', 'crimson',  'darkred' , 'darkslategray', 
        'violet', 'mediumvioletred' ,'orchid','tomato' , 'coral', 'goldenrod', 'tan', 'peru',  'sienna',
        'rosybrown','darkgoldenrod','navajowhite','darkkhaki','darkseagreen' ,'firebrick','lightsteelblue']

MARKERS = {
	1.0 :'+',2.0: 'x',5.5:'s',6.5:'o',11.0:'^',
	13.0:'H',18.0:'>',19.5:'h',26.0:'v',36.0:'p',
	39.0:'<',48.0:'*',54.0:'D',52.0:'1',58.5:'2',
	65.0:'3',78.0:'4',117.0 :'8',130.0:'_',
	104.0:'|',6.0:'_',45.0:'|',60.0:'_',40.5:'|',
	135:'|', 270.0:'|',108.0:'|',120.0:'_'
	}



MARKERS_2 = {
	1.0 :'o',2.0: 'o',5.5:'o',6.5:'o',11.0:'o',
	13.0:'o',18.0:'o',19.5:'o',26.0:'o',36.0:'o',
	39.0:'o',48.0:'o',54.0:'o',52.0:'o',58.5:'o',
	65.0:'o',78.0:'o',117.0 :'o',130.0:'o',
	104.0:'o',6.0:'o', 
	}

#1,2,3,4,- -, --, -. : . o,v , H h d | _
'''
testing dataset :
retx_rate_table = {
    'OWC43DC7B0AE78' : [[54.0,1],[36.0,2],[5.5,3],],
    'OWC43DC7A3EDEC' : [[54.0,1],[36.0,2],[5.5,3],],
    'OWC43DC7B0AE54' :[[54.0,1],[18.0,2],[5.5,3],],
    'OWC43DC7A3F0D4' :[[54.0,1],[36.0,2],[18.0,3],],
    'OWC43DC7A37C01' :[[54.0,4],[36.0,5],[5.5,6],],
    'OWC43DC7B0AE1B' :[[54.0,8],[1.0,7],[5.5,6],],
    'OWC43DC79DE112' :[[54.0,9],[2.0,10],[5.5,11],],
    'OWC43DC7B0AE69' :[[54.0,8],[36.0,11],[5.5,13],],
    'OWC43DC7A3EE22' :[[54.0,3],[48.0,1],[5.5,4],],        
    }

contention_table = {
    'OWC43DC7B0AE78' : [157,13.3,312,523,123,5235,55111,2424,54],
    'OWC43DC7A3EDEC' : [155,123.3,312,23,121,3523,14235,2424,554],
    'OWC43DC7B0AE54' : [165,123.3,312,523,123,5235,24525,2424,554],
    'OWC43DC7A3F0D4' : [345,123.3,523,123,5235,125,2242,52354,134],
    'OWC43DC7A37C01' : [253,123.3,312,523,123,5235,12452,2424,5254],
    'OWC43DC7B0AE1B' : [157,123.3,312,523,123,5223,24243,52354,134],
    'OWC43DC79DE112' : [333,123.3,312,523,123,5235,12455,2424,5254],
    'OWC43DC7B0AE69' : [329,123.3,312,523,123,5235,12455,2424,5254],
    'OWC43DC7A3EE22' : [173,123.3,312,523,123,5235,12455,2424,5254],
    }
'''

def plotter_scatter(x_axis,y_axis,x_axis_label,y_axis_label,x_logscale,y_logscale):
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
            a = _subplot.scatter(rates_array[val][1],median(contention_table[key]),s=50,color=color[index],marker=MARKERS[rates_array[val][0]],label=lp)
            #_subplot.boxplot(contention_table[key]),positions=rates_array[val][1])
            if rates_array[val][0] in rates_encountered:
                pass
            else:
                rates_encountered.append(rates_array[val][0])                
                li.append(a)
        index = index+1        
    legend2=_subplot.legend(li,MARKERS,bbox_to_anchor=(0.9,-0.05), prop=LEGEND_PROP,loc=2)
    _subplot.add_artist(legend2)
    _subplot.legend(loc=0, prop=LEGEND_PROP,bbox_to_anchor=(0.1,- 0.05),scatterpoints=1)
    _subplot.set_ylabel(y_axis_label)
    _subplot.set_xlabel(x_axis_label)

    if x_logscale :
        _subplot.set_xscale('log')
    if y_logscale :
        _subplot.set_yscale('log')
    _subplot.set_xlim([0,1])
    canvas = FigureCanvasAgg(fig)
    if '.eps' in outfile_name:
        canvas.print_eps(outfile_name, dpi = 110)
    if '.png' in outfile_name:
        canvas.print_figure(outfile_name, dpi = 110)

def retx_map(_tx,_retx,threshold,router_id):
    retx_list_list=[]
    for k,v in _tx.iteritems():
        if k in _retx :
            print k, "is in home_retx"
            if v> threshold:
                ratio=_retx[k]*1.0/v
                retx_list_list.append([k,ratio])
            else :
                pass
        else :
            print k ,"is not in home_retx"
            if v> threshold:
                retx_list_list.append([k,0.0])
    for k,v in _retx.iteritems():
        if not (k in _tx):
            if v> threshold:
                retx_list_list.append([k,v*1.0])

    return retx_list_list


def pickle_reader(input_folder,threshold):
    print "the pickle reader called " 
    data_fs=os.listdir(input_folder)
    c_table={}
    retx_norm_table=defaultdict(list)
    for f_name in data_fs :
	_f_content= pickle.load(open(input_folder+f_name,'rb'))
	router_id= _f_content[0]
	retransmission_count_table=_f_content[1]
	transmission_count_table=_f_content[2]
	contention_time=_f_content[3]
	c_table[router_id]=contention_time
	retx_norm_table[router_id]=retx_map(transmission_count_table,retransmission_count_table,threshold,router_id)
    return [c_table,retx_norm_table]	
if __name__=='__main__':    
    if len(sys.argv) !=3:
        print "usage : python unpickeler.py data_folder filename.png  "
        sys.exit(0)
    outfile_name = sys.argv[2]
    input_folder = sys.argv[1]
    #path=sys.argv[2] #of pickle files 
    if '.eps' not in outfile_name and '.png' not in outfile_name:
        print "Do you really want to write graph to %s?" % (outfile_name)
        sys.exit(0)
    
    [contention_table,retx_rate_table]=pickle_reader(input_folder,1000)
    print len(contention_table.keys())
    print "========="
    print retx_rate_table
    
    plotter_scatter(retx_rate_table,
        contention_table,
        'retransmits(no. of frames retransmitted /no. of successful transmissions)',
        'Contention Delay(microsecond)',
                    0,
                    0)
