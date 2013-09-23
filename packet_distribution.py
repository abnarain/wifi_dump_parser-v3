#Author : Abhinav Narain
#Date : Aug 26, 2013
#Purpose : To read the binary files with data from BISmark deployment in homes
# Gives the packet sizes of the frames received by the BISmark Access Point
# Creates a map of the Access Class of frames transmitted for each device inside home

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

tx_timeseries=[]

def file_reader(t1,t2,data_fs):
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
                        pass
                    elif radiotap_len==RADIOTAP_TX_LEN :
                        # 12 is device mac address, 
                        tx_timeseries.append(temp)
            else:
                print "success denied; incorrect data frame"
                damaged_frames +=1
            data_index=data_index+DATA_STRUCT_SIZE
            del frame_elem
            del monitor_elem

        if file_count %10 == 0:
            print file_count

if 0:#__name__=='__main__':
    '''
    This main plots the distribution of packets on each of the access class transmit queues in 
    hardware in the ath9k driver 
    '''
    if len(sys.argv) !=6 :
	print len(sys.argv)
	print "Usage : python station-process.py data/<data.gz> <router_id> <t1> <t2> <outputfile> "
	sys.exit(1)
    data_f_dir=sys.argv[1]
    router_id= sys.argv[2]
    time1 =sys.argv[3]
    time2 =sys.argv[4]
    output_folder=sys.argv[5]
    data_fs=os.listdir(data_f_dir)
    [t1,t2] = timeStamp_Conversion(time1,time2,router_id)
    data_file_header_byte_count=0
    filename_list=[]
    damaged_frames=0
    unix_time=set()
    print "now processing the files to calculate time "
    file_reader(t1,t2,data_fs)
    Station_list=list(Station)
    Station_access_class_map=defaultdict(list)
    for s in Station_list:
        access_class=defaultdict(int)
        for frame_element in tx_timeseries: 
            if s == frame_element[12]:
                access_class[frame_element[8]] +=1
        keys_to_delete=[]        
        for k,v in access_class.iteritems():
            if v <600:
                keys_to_delete.append(k)
        for key in keys_to_delete :
            del access_class[key]
        if len(access_class.keys())>0:     
            Station_access_class_map[s].append(access_class)
    from magicplott import *
    print Station_access_class_map
    x_axes,y_axes,device_ids=[],[],[]
    for device_id, hw_queue_map  in Station_access_class_map.iteritems():
        device_ids.append(device_id)
        x_axis,y_axis=[],[]        
        print "hw map for ",device_id, "is ", hw_queue_map
        x_axis=hw_queue_map[0].keys()
        x_axis.sort()
        x_axes.append(x_axis)
        for i in x_axis :
            y_axis.append(hw_queue_map[0][i])
        y_axes.append(y_axis)
        bar_graph_subplots(device_ids,
                           x_axes,y_axes,
                           'Hardware Queue No/ Access Class',
                           'Frames tx from the Queue',
                           'Distribution of wireless traffic into 802.11 Access Class',
                            output_folder+router_id+'_access_class_distr.png')
    print "damage frame count " , damaged_frames
    # 0      ,1          ,2     ,3              ,4            ,5        ,6          ,7       ,8          ,9                ,10        ,11
    #time [0],txflags[1],retx[2],success_rate[3],total_time[4],Q len [5],A-Q len [6], Q-no[7],phy_type[8],retx_rate_list[9],seq no[13],fragment no[14],mac-layer-flags[15], farme-prop-type[16], framesize[17],
# 12                  ,13                  ,14
#    print "dictionary is ",dic

ampdu_dynamics,mpdu_dynamics=defaultdict(list), defaultdict(list)
def Queue_file_reader(t1,t2,data_fs):
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
                        pass
                    elif radiotap_len==RADIOTAP_TX_LEN :
                        # 12 is device mac address, 
                        ampdu_dynamics[data_file_current_timestamp].append(temp[6])
                        mpdu_dynamics[data_file_current_timestamp].append(temp[5])
            else:
                print "success denied; incorrect data frame"
                damaged_frames +=1
            data_index=data_index+DATA_STRUCT_SIZE
            del frame_elem
            del monitor_elem

        if file_count %10 == 0:
            print file_count



if __name__=='__main__':
    '''
    This main plots the dynamics of driver queue every minute
    '''
    if len(sys.argv) !=6 :
	print len(sys.argv)
	print "Usage : python station-process.py data/<data.gz> <router_id> <t1> <t2> <outputfile> "
	sys.exit(1)
    data_f_dir=sys.argv[1]
    router_id= sys.argv[2]
    time1 =sys.argv[3]
    time2 =sys.argv[4]
    output_folder=sys.argv[5]
    data_fs=os.listdir(data_f_dir)
    [t1,t2] = timeStamp_Conversion(time1,time2,router_id)
    data_file_header_byte_count=0
    filename_list=[]
    damaged_frames=0
    unix_time=set()
    print "now processing the files to calculate time "
    Queue_file_reader(t1,t2,data_fs)
    timeseries_mpdu,timeseries_ampdu,mpdu_list,ampdu_list=[],[],[],[]
    for timestamp, list_mpdu_lens in mpdu_dynamics.iteritems():
         timeseries_mpdu.append(timestamp), mpdu_list.append(max(list_mpdu_lens))

    for timestamp, list_ampdu_lens in mpdu_dynamics.iteritems():
         timeseries_ampdu.append(timestamp), ampdu_list.append(max(list_ampdu_lens))
    
    print "damage frame count " , damaged_frames

