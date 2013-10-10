#Author : Abhinav Narain
#Date : 5-sept-2013
#Purpose : To plot the scatter plot of bitrates observed in a home
# vs the wireless contention inside homes 


from magicplott import *

def pickle_reader(input_folder,threshold):

    '''
    testing dataset format :
    retx_rate_table = {
    'OWC43DC7B0AE78' : [[54.0,1],[36.0,2],[5.5,3],],
    'OWC43DC7A3EDEC' : [[54.0,1],[36.0,2],[5.5,3],],
    'OWC43DC7A3EE22' :[[54.0,3],[48.0,1],[5.5,4],],        
    }
    
    contention_table = {
    'OWC43DC7B0AE78' : [157,13.3,312,523,123,5235,55111,2424,54],
    'OWC43DC7A3EDEC' : [155,123.3,312,23,121,3523,14235,2424,554],
    'OWC43DC7A3EE22' : [173,123.3,312,523,123,5235,12455,2424,5254],
    }
    '''

    '''
    reads the pickle file by contention-data-frame-calc to fetch required data
    '''    
    def retx_map(_tx,_retx,threshold):
        '''
        transmforms the counts to a fraction if the frame
        count is above a threshold
        '''
        retx_list_list=[]
        for k,v in _tx.iteritems():
            if k in _retx :
                if v> threshold:
                    ratio=_retx[k]*1.0/v
                    retx_list_list.append([k,ratio])
                else :
                    pass
            else :
                if v> threshold:
                    retx_list_list.append([k,0.0])
        for k,v in _retx.iteritems():
            if not (k in _tx):
                if v> threshold:
                    retx_list_list.append([k,v*1.0])

        return retx_list_list

    data_fs=os.listdir(input_folder)
    c_table={}
    undersampled_rate_list=[]
    retx_norm_table=defaultdict(list)
    for f_name in data_fs :
	_f_content= pickle.load(open(input_folder+f_name,'rb'))
	router_id= _f_content[0]
	retransmission_count_table=_f_content[1]
	transmission_count_table=_f_content[2]
	contention_time=_f_content[3]
	c_table[router_id]=contention_time
        l=retx_map(transmission_count_table,retransmission_count_table,threshold)
        if len(l)==0:
            print router_id
            print len(l)
            undersampled_rate_list.append(router_id)
        else :
            retx_norm_table[router_id]=l

    return [c_table,retx_norm_table,undersampled_rate_list]	


def contention_data_pickle_reader(contention_data_input_folder):
    '''
    reads the pickle file by contention-data-frame-calc to fetch
    only the contention period observed at AP
    '''
    data_fs=os.listdir(contention_data_input_folder)
    home_contention_table=defaultdict(list)
    for f_name in data_fs :
        #router_id,ap_macs,device_macs,ap_map,device_map,rate_map ; maps are of times 
	_f_content= pickle.load(open(contention_data_input_folder+f_name,'rb'))
	router_id= _f_content[0]
        retransmission_count_table=_f_content[1]
        frame_count_table=_f_content[2]
        contention_time=_f_content[3]
        home_contention_table[router_id]=contention_time
    return home_contention_table

def contention_per_access_class_data_pickle_reader(contention_data_input_folder):
    '''
    reads the pickle file by contention-data-frame-calc to fetch
    contention period dictionary per access class  observed at AP
    '''
    data_fs=os.listdir(contention_data_input_folder)
    home_contention_table=defaultdict(list)
    for f_name in data_fs :
        #router_id,ap_macs,device_macs,ap_map,device_map,rate_map ; maps are of times 
	_f_content= pickle.load(open(contention_data_input_folder+f_name,'rb'))
	router_id= _f_content[0]
    contention_time_per_access_class=_f_content[1]
    home_contention_table[router_id]=contention_time_per_access_class
    return home_contention_table


def device_count_pickle_reader(input_folder):
    '''
    fetches the data from pickle file dumped by device-count-process.py
    '''
    data_fs=os.listdir(input_folder)
    home_device_table=defaultdict(list)
    home_ap_table=defaultdict(list)
    for f_name in data_fs :
        #router_id,ap_macs,device_macs,ap_map,device_map,rate_map ; maps are of times 
	_f_content= pickle.load(open(input_folder+f_name,'rb'))
	router_id= _f_content[0]
        ap_mac=_f_content[1]
        device_mac=_f_content[2]
        home_device_table[router_id]=device_mac
        home_ap_table[router_id]=ap_mac
        
    return [home_ap_table,home_device_table]

def per_station_data_pickle_reader(home_packet_dump_input_folder,router_id):
    '''
    reads the packet trace into a dictionary for all stations for a home    
    '''
    data_fs=os.listdir(home_packet_dump_input_folder)
    home_packet_dump_table=defaultdict(list)
    for f_name in data_fs :
    #router_id,ap_macs,device_macs,ap_map,device_map,rate_map ; maps are of times 
        print f_name
        if f_name.split('.')[0]==router_id :
           _f_content= pickle.load(open(home_packet_dump_input_folder+f_name,'rb'))
           if not (router_id==_f_content[0]):
               print "there is a problem in router id... exit" 
               sys.exit(1)
           home_packet_dump_map=_f_content[1]
           return home_packet_dump_map

    print "The routerId is not in folder" 

if 0: #__name__=='__main__':
    '''
    This main plots the scattterplot of contetion time with the avg retransmission count
    '''
    if len(sys.argv) !=3:
        print "usage : python unpickeler.py <data_folder> <filename.png>  "
        sys.exit(0)
    outfile_name = sys.argv[2]
    input_folder = sys.argv[1]
    if '.eps' not in outfile_name and '.png' not in outfile_name:
        print "Do you really want to write graph to %s?" % (outfile_name)
        sys.exit(0)
    [contention_table,retx_rate_table,undersampled_rate_list]=pickle_reader(input_folder,1000)
    for k in undersampled_rate_list :
        try :
            del contention_table[k]
        except :
            print k, " is not present in contention_table"
    for k in undersampled_rate_list :
        try :
            del retx_rate_table[k]
        except :
            print k, " is not present in contention_table"
            
    print "after" ,  len(contention_table)
    print "of retx" , len(retx_rate_table)
    print "========="
    print retx_rate_table
    
    plotter_scatter(retx_rate_table,
                    contention_table,
                    'retransmits(no. of frames retransmitted /no. of successful transmissions)',
                    'Contention Delay(microsecond) 90th percentile',
                    0,
                    0,
                    'Scatterplot for retransmission vs Contention Delay in homes for 5GHz band',
                    outfile_name)


def contention_general(home_contention_table,home_ap_2_table,home_device_2_table,outfile_name):
    '''
    Plots the distribution of contention in every home. It does not take into account every
    access class (and the variation due AIFS)
    '''
    router_list=[]
    x_axis_ap_counts=[]
    y_axis_contention_array=[]

    for router_id,ap_count in home_ap_2_table.iteritems():
        if router_id in home_contention_table.keys():
            if len(home_contention_table[router_id]) >1000: # more than 1000 sample points
                router_list.append(router_id)
                x_axis_ap_counts.append(len(ap_count))
                y_axis_contention_array.append(home_contention_table[router_id])

    scatter_simply(router_list,x_axis_ap_counts,y_axis_contention_array,
                   'Access Point Count',
                   'Contention Period (90th percentile) in microseconds',
                   'Variation of Contention Period with #Access Points in vicinity (2.4 GHz)',
                   outfile_name+'_ap_count.png',[0,70],[0,16000])
    

    router_list=[]
    x_axis_ap_counts=[]
    y_axis_contention_array=[]
    for router_id,ap_count in home_device_2_table.iteritems():
        if router_id in home_contention_table.keys():
            if len(home_contention_table[router_id]) >1000: # more than 1000 sample points
                router_list.append(router_id)
                x_axis_ap_counts.append(len(ap_count))
                y_axis_contention_array.append(home_contention_table[router_id])

    scatter_simply(router_list,x_axis_ap_counts,y_axis_contention_array,
                   'Number of devices inside homes ',
                   'Contention Period (90th percentile) in microseconds',
                   'Variation of Contention Period with #Devices in vicinity (2.4 GHz)',
                   outfile_name+'_device_count.png',[0,400],[0,16000])


def contention_per_access_class(contention_per_access_class_table,home_ap_2_table,home_device_2_table,outfile_name):
    '''
    Plots the distribution of contention in every home for every access class (VO/VI/BE/BK)
    '''
    for i,j in  contention_per_access_class_table.iteritems():
        for t,n in j.iteritems():
            print t,len(n)
    '''
    router_list=[]
    x_axis_ap_counts=[]
    y_axis_contention_array=[]

    for router_id,ap_count in home_ap_2_table.iteritems():
        if router_id in home_contention_table.keys():
            if len(home_contention_table[router_id]) >1000: # more than 1000 sample points
                router_list.append(router_id)
                x_axis_ap_counts.append(len(ap_count))
                y_axis_contention_array.append(home_contention_table[router_id])

    scatter_simply(router_list,x_axis_ap_counts,y_axis_contention_array,
                   'Access Point Count',
                   'Contention Period (90th percentile) in microseconds',
                   'Variation of Contention Period with #Access Points in vicinity (2.4 GHz)',
                   outfile_name+'_ap_count.png',[0,70],[0,16000])
    

    router_list=[]
    x_axis_ap_counts=[]
    y_axis_contention_array=[]
    for router_id,ap_count in home_device_2_table.iteritems():
        if router_id in home_contention_table.keys():
            if len(home_contention_table[router_id]) >1000: # more than 1000 sample points
                router_list.append(router_id)
                x_axis_ap_counts.append(len(ap_count))
                y_axis_contention_array.append(home_contention_table[router_id])

    scatter_simply(router_list,x_axis_ap_counts,y_axis_contention_array,
                   'Number of devices inside homes ',
                   'Contention Period (90th percentile) in microseconds',
                   'Variation of Contention Period with #Devices in vicinity (2.4 GHz)',
                   outfile_name+'_device_count.png',[0,400],[0,16000])
    '''

def bitrate_scatter_plot():
    '''
    The function plots the bitrate scatter plot for upstream and downstream 
    plots
    '''
#TODO : This function is incomplete and needs to be coded !!!
    #Alex asked to :remove cases with retransmission
#    if len(packet_array[i][1])== 4 : # received frame  8 is the bitrate
#    elif len(packet_array[i][0])== 5 : #transmitted frame 3 is bitrate


if  __name__ == '__main__': 
    '''
    Plot the Scatterplot of Contention time delay vs the Number of Access Points scatterplot 
    '''
    if len(sys.argv) !=4:
        print "usage : python unpickeler.py <contention_data_folder_2GHz>  <ap_device_count_data_folder> <filename.png>  "
        sys.exit(0)
    contention_data_input_folder = sys.argv[1]
    access_point_data_input_folder = sys.argv[2]
    outfile_name = sys.argv[3]
    home_ap_2_table=defaultdict(list)
    home_device_2_table=defaultdict(list)
    contention_per_access_class_table=defaultdict(list)
    [home_ap_2_table,home_device_2_table]=device_count_pickle_reader(access_point_data_input_folder)
    if 0:
        home_contention_table=defaultdict(list)
        home_contention_table=contention_data_pickle_reader(contention_data_input_folder)
        contention_general(home_contention_table,home_ap_2_table,home_device_2_table,outfile_name)
    print "reading table of contention"
    contention_per_access_class_table=contention_per_access_class_data_pickle_reader(contention_data_input_folder)
    print "going to plot " 
    contention_per_access_class(contention_per_access_class_table,home_ap_2_table,home_device_2_table,outfile_name)
    
    #bitrate_scatter_plot(t1,t2,data_fs)
    #home_packet_dump_map=per_station_data_pickle_reader(_folder,router_id)
