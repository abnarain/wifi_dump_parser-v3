#Author : Abhinav Narain
#Date : Sept 17, 2013
#Purpose : To read the binary files with data from BISmark deployment in homes
# Gives the rates used by all devices in the network where the Bismark Access Point is installed
#  

import os,sys,re
import gzip
import struct 
from collections import defaultdict

from  header import *
from mac_parser import * 
from utils import *
from rate import * 

try:
    import cPickle as pickle
except ImportError:
    import pickle

rate_distribution=defaultdict(int)

def all_devices_rates_file_reader(t1,t2,data_fs):
    global damaged_frames
    file_count=0
    for data_f_n in data_fs :
        filename_list.append(data_f_n.split('-'))
        unix_time.add(int(data_f_n.split('-')[1]))
        if not (data_f_n.split('-')[2]=='d'):
            print "its not a data file ; skip "
            continue 

    filename_list.sort(key=lambda x : int(x[3]))
    filename_list.sort(key=lambda x : int(x[1]))
    tt=0
    for data_f_name_list in filename_list : #data_fs :    
        file_count=file_count+1
        data_f_name="-".join(data_f_name_list)
        data_f= gzip.open(data_f_dir+data_f_name,'rb')
        data_file_content=data_f.read()
        data_f.close()
        data_file_current_timestamp=0
        data_file_seq_n=0
        bismark_id_data_file=0
        start_64_timestamp_data_file=0
        for i in xrange(len(data_file_content )):
            if data_file_content[i]=='\n':
                bismark_data_file_header = str(data_file_content[0:i])
                ents= bismark_data_file_header.split(' ')
                bismark_id_data_file=ents[0]
                start_64_timestamp_data_file= int(ents[1])
                data_file_seq_no= int(ents[2])
                data_file_current_timestamp=int(ents[3])
                data_file_header_byte_count =i
                break

        data_contents=data_file_content.split('\n----\n')
        header_and_correct_data_frames = data_contents[0]
        err_data_frames = data_contents[1]
        correct_data_frames_missed=data_contents[2]
        err_data_frames_missed=data_contents[3]

    #done with reading the binary blobs from file ; now check for timestamps are correct
        '''
        if  (data_file_current_timestamp < t1-1):
            continue 
        if (data_file_current_timestamp >t2+1):
            break 
        '''
        correct_data_frames=header_and_correct_data_frames[data_file_header_byte_count+1:]
        data_index=0
        for idx in xrange(0,len(correct_data_frames)-DATA_STRUCT_SIZE ,DATA_STRUCT_SIZE ):	
            frame=correct_data_frames[data_index:data_index+DATA_STRUCT_SIZE]
            offset,success,tsf= 8,-1,0
            header = frame[:offset]
            frame_elem=defaultdict(list)
            monitor_elem=defaultdict(list)        
            (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
            (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)  
            if success==1:
                for key in frame_elem.keys():
                    tsf=key                                    
                    parse_data_frame(frame,radiotap_len,frame_elem)
                    if radiotap_len ==RADIOTAP_RX_LEN :
                        rate_distribution[frame_elem[tsf][7]] +=1
                    elif radiotap_len==RADIOTAP_TX_LEN :
                        rate_distribution[frame_elem[tsf][2]] +=1
                    else :
                        print "data frame: impossible radiotap len"
            else:
                print "success denied; incorrect data frame"
                damaged_frames +=1
            data_index=data_index+DATA_STRUCT_SIZE
            del frame_elem
            del monitor_elem
        
        data_index=0
        for idx in xrange(0,len(err_data_frames)-DATA_ERR_STRUCT_SIZE,DATA_ERR_STRUCT_SIZE ):   
            frame=err_data_frames[data_index:data_index+DATA_ERR_STRUCT_SIZE]
            offset,success,tsf= 8,-1,0
            header = frame[:offset]
            frame_elem=defaultdict(list)
            monitor_elem=defaultdict(list)
            (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
            (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
            if success==1:
                for key in frame_elem.keys():
                    tsf=key
                parse_err_data_frame(frame,radiotap_len,frame_elem)
                if radiotap_len == RADIOTAP_RX_LEN:                                    
                    rate_distribution[frame_elem[tsf][7]] +=1
                elif radiotap_len ==RADIOTAP_TX_LEN :
                    print "err tx", frame_elem
                    sys.exit(1)
                else :
                    print "impossible radiotap len detected ; Report CERN"             
            else :
                print "success denied; incorrect data frame" 
                   
            data_index= data_index+DATA_ERR_STRUCT_SIZE
            del frame_elem
            del monitor_elem    
        
        if file_count %10 == 0:
            print file_count


tx_timeseries,rx_timeseries=[],[]
def connected_devices_rates_file_reader(t1,t2,data_fs):
    global damaged_frames
    file_count=0
    for data_f_n in data_fs :
        filename_list.append(data_f_n.split('-'))
        unix_time.add(int(data_f_n.split('-')[1]))
        if not (data_f_n.split('-')[2]=='d'):
            print "its not a data file ; skip "
            continue 

    filename_list.sort(key=lambda x : int(x[3]))
    filename_list.sort(key=lambda x : int(x[1]))
    tt=0
    for data_f_name_list in filename_list : #data_fs :    
        file_count=file_count+1
        data_f_name="-".join(data_f_name_list)
        data_f= gzip.open(data_f_dir+data_f_name,'rb')
        data_file_content=data_f.read()
        data_f.close()
        data_file_current_timestamp=0
        data_file_seq_n=0
        bismark_id_data_file=0
        start_64_timestamp_data_file=0
        for i in xrange(len(data_file_content )):
            if data_file_content[i]=='\n':
                bismark_data_file_header = str(data_file_content[0:i])
                ents= bismark_data_file_header.split(' ')
                bismark_id_data_file=ents[0]
                start_64_timestamp_data_file= int(ents[1])
                data_file_seq_no= int(ents[2])
                data_file_current_timestamp=int(ents[3])
                data_file_header_byte_count =i
                break

        data_contents=data_file_content.split('\n----\n')
        header_and_correct_data_frames = data_contents[0]
        err_data_frames = data_contents[1]
        correct_data_frames_missed=data_contents[2]
        err_data_frames_missed=data_contents[3]

    #done with reading the binary blobs from file ; now check for timestamps are correct
        '''
        if  (data_file_current_timestamp < t1-1):
            continue 
        if (data_file_current_timestamp >t2+1):
            break 
        '''
        correct_data_frames=header_and_correct_data_frames[data_file_header_byte_count+1:]
        data_index=0
        for idx in xrange(0,len(correct_data_frames)-DATA_STRUCT_SIZE ,DATA_STRUCT_SIZE ):	
            frame=correct_data_frames[data_index:data_index+DATA_STRUCT_SIZE]
            offset,success,tsf= 8,-1,0
            header = frame[:offset]
            frame_elem=defaultdict(list)
            monitor_elem=defaultdict(list)        
            (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
            (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)  
            if success==1:
                for key in frame_elem.keys():
                    tsf=key                                    
                    parse_data_frame(frame,radiotap_len,frame_elem)
                    temp=frame_elem[tsf]
                    temp.insert(0,tsf)
                    if radiotap_len ==RADIOTAP_RX_LEN :
                        rx_timeseries.append(temp)
                    elif radiotap_len==RADIOTAP_TX_LEN :
                        tx_timeseries.append(temp)
                    else :
                        print "data frame: impossible radiotap len"
            else:
                print "success denied; incorrect data frame"
                damaged_frames +=1
            data_index=data_index+DATA_STRUCT_SIZE
            del frame_elem
            del monitor_elem
        
        data_index=0

        for idx in xrange(0,len(err_data_frames)-DATA_ERR_STRUCT_SIZE,DATA_ERR_STRUCT_SIZE ):   
            frame=err_data_frames[data_index:data_index+DATA_ERR_STRUCT_SIZE]
            offset,success,tsf= 8,-1,0
            header = frame[:offset]
            frame_elem=defaultdict(list)
            monitor_elem=defaultdict(list)
            (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
            (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
            if success==1:
                for key in frame_elem.keys():
                    tsf=key
                parse_err_data_frame(frame,radiotap_len,frame_elem)
                temp=frame_elem[tsf]
                temp.insert(0,tsf)
                if radiotap_len == RADIOTAP_RX_LEN:                                    
                    rx_timeseries.append(temp)
                elif radiotap_len ==RADIOTAP_TX_LEN :
                    print "THIS IS err tx",frame_elem
                    sys.exit(1)
                else :
                    print "impossible radiotap len detected ; Report CERN"             
            else :
                print "success denied; incorrect data frame" 
                   
            data_index= data_index+DATA_ERR_STRUCT_SIZE
            del frame_elem
            del monitor_elem    
        
        if file_count %10 == 0:
            print file_count

def plot_all_devices():
    import operator
    #print max(rate_distribution.iteritems(), key=operator.itemgetter(1))[0]
    max_freq= rate_distribution[max(rate_distribution.iteritems(), key=operator.itemgetter(1))[0]]
    for k,v in rate_distribution.iteritems():
        v = v*1.0/ max_freq
        rate_distribution[k]=v
    x_axis=rate_distribution.keys()
    x_axis.sort()
    y_axis=[]
    for i in range(0,len(x_axis)):
        y_axis.append( rate_distribution[x_axis[i]])        
    from magicplott import *
    bar_graph_plotter(x_axis,
                      y_axis,
                      '802.11 bitrates',
                      'Normalized frequency of occurence of bitrate',
                      'Distribution of bitrates of all devices in a Home Network(' +router_id+')',
                      output_file+router_id+'_bitrate_dist_2_4.png')

def process_connected_devices():
    pass

if __name__=='__main__':
    if len(sys.argv) !=6 :
	print len(sys.argv)
	print "Usage : python station-process.py data/<data.gz> <router_id> <t1> <t2> <outputfile> "
	sys.exit(1)
    data_f_dir=sys.argv[1]
    router_id= sys.argv[2]
    time1 =sys.argv[3]
    time2 =sys.argv[4]
    output_file=sys.argv[5]
    data_fs=os.listdir(data_f_dir)
    [t1,t2] = timeStamp_Conversion(time1,time2,router_id)
    data_file_header_byte_count=0
    filename_list=[]
    damaged_frames=0
    unix_time=set()
    print "now processing the files to calculate time "
    #to process rate distribution of complete home 
    #all_devices_rates_file_reader(t1,t2,data_fs)
    #plot_all_devices()
    connected_devices_rates_file_reader(t1,t2,data_fs)
    rx_timeseries.sort(key=lambda x:x[0])
    tx_timeseries.sort(key=lambda x:x[0])
    Station_list=list(Station)
    for j in range(0,len(Station_list)):
        for i in range(0,len(tx_timeseries)):
            frame = tx_timeseries[i]
            print frame
            if frame[12]==Station_list[j] :
                pass
