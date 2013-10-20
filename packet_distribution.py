#Author : Abhinav Narain
#Date : Aug 26, 2013
#Purpose : To read the binary files with data from BISmark deployment in homes
# Gives the packet sizes of the frames received by the BISmark Access Point
# Creates a map of the Access Class of frames transmitted for each device inside home (into AC_VI,AC_VO, AC_BE, AC_BG, AC_MU
# Plots distribution of qeueue length (in number of packets (not bytes) with time

import os,sys,re
import gzip
import struct 
from collections import defaultdict

from  header import *
from mac_parser import * 
from utils import *
from rate import * 
from magicplott import *

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
        start_64_timestamp_data_file=0
        for i in xrange(len(data_file_content )):
            if data_file_content[i]=='\n':
                bismark_data_file_header = str(data_file_content[0:i])
                ents= bismark_data_file_header.split(' ')
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

def per_queue_classification(t1,t2,data_fs):
    '''
    This main plots the distribution of packets on each of the access class transmit queues in 
    hardware in the ath9k driver 
    '''
    data_file_header_byte_count=0
    filename_list=[]
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
def queue_file_reader(t1,t2,data_fs):
    '''
    Stores the size of ampdu and mpdu queues in a dictionary
    '''
    global damaged_frames
    file_count=0
    for data_f_n in data_fs :
        filename_list.append(data_f_n.split('-'))
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


timeseries_pkt_size_rate=defaultdict(list)
def total_file_content_reader(t1,t2,data_fs,data_f_dir):
     ctrl_dir_components= data_f_dir.split('/')
     ctrl_dir_components[-2]=re.sub('data','ctrl',ctrl_dir_components[-2]) 
     ctrl_f_dir="/".join(ctrl_dir_components)
     mgmt_dir_components= data_f_dir.split('/')
     mgmt_dir_components[-2]=re.sub('data','mgmt',mgmt_dir_components[-2]) 
     mgmt_f_dir="/".join(mgmt_dir_components)
     print mgmt_f_dir
     print ctrl_f_dir
     global damaged_frames
     missing_files=[]
     file_count=0
     for data_f_n in data_fs :
         filename_list.append(data_f_n.split('-'))
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

         ctrl_f_name = data_f_name
         ctrl_f_name =re.sub("-d-","-c-",ctrl_f_name)

         try :
             ctrl_f= gzip.open(ctrl_f_dir+ctrl_f_name,'rb')	
             ctrl_file_content=ctrl_f.read()
         except :
             print  "CTRL file not present ", ctrl_f_name 
             missing_files.append([ctrl_f_name,data_file_current_timestamp])
             continue 
         ctrl_f.close()
        
        
         mgmt_f_name = data_f_name
         mgmt_f_name = re.sub("-d-","-m-",mgmt_f_name)
         try : 
             mgmt_f= gzip.open(mgmt_f_dir+mgmt_f_name,'rb')
             mgmt_file_content=mgmt_f.read()
         except :
             print "MGMT file not present ",mgmt_f_name 
             missing_files.append([mgmt_f_name,data_file_current_timestamp])
             continue 

         mgmt_f.close()

         mgmt_file_current_timestamp=0
         mgmt_file_seq_no=0
         bismark_id_mgmt_file=0
         start_64_timestamp_mgmt_file=0
        
         ctrl_file_current_timestamp=0
         ctrl_file_seq_no=0
         bismark_id_ctrl_file=0
         start_64_timestamp_ctrl_file=0

         for i in xrange(len(mgmt_file_content )):
             if mgmt_file_content[i]=='\n':
                 bismark_mgmt_file_header = str(mgmt_file_content[0:i])
                 ents= bismark_mgmt_file_header.split(' ')
                 bismark_id_mgmt_file=ents[0]
                 start_64_timestamp_mgmt_file=int(ents[1])
                 mgmt_file_seq_no= int(ents[2])
                 mgmt_file_current_timestamp= int(ents[3])
                 mgmt_file_header_byte_count =i
                 break
         mgmt_contents=mgmt_file_content.split('\n----\n')
         header_and_beacon_mgmt_frames = mgmt_contents[0] 
         common_mgmt_frames = mgmt_contents[1]
         err_mgmt_frames=mgmt_contents[2]
         beacon_mgmt_frames_missed=mgmt_contents[3]
         common_mgmt_frames_missed=mgmt_contents[4]
         err_mgmt_frames_missed=mgmt_contents[5]

         for i in xrange(len(ctrl_file_content )):
             if ctrl_file_content[i]=='\n':
                 bismark_ctrl_file_header = str(ctrl_file_content[0:i])
                 ents= bismark_ctrl_file_header.split(' ')
                 bismark_id_ctrl_file= ents[0]
                 start_64_timestamp_ctrl_file= int(ents[1])
                 ctrl_file_seq_no= int(ents[2])
                 ctrl_file_current_timestamp=int(ents[3])
                 ctrl_file_header_byte_count =i
                 break
         ctrl_contents=ctrl_file_content.split('\n----\n')
         header_and_correct_ctrl_frames = ctrl_contents[0]
         err_ctrl_frames = ctrl_contents[1]
         correct_ctrl_frames_missed=ctrl_contents[2]
         err_ctrl_frames_missed=ctrl_contents[3]
        #done with reading the binary blobs from file ; now check for timestamps are correct
         if (not (ctrl_file_current_timestamp == mgmt_file_current_timestamp == data_file_current_timestamp )) :
             print "timestamps don't match ", data_f_name
             sys.exit(1)
         else :
             file_timestamp=ctrl_file_current_timestamp
         if (not (ctrl_file_seq_no == mgmt_file_seq_no == data_file_seq_no)):
             print "sequence number don't match "
             sys.exit(1)
 
         if (len(ctrl_contents) != 4 or  len(data_contents) != 4 or len(mgmt_contents) !=6) :
             print "for ctrl " ,len (ctrl_contents) ,"for data", len(data_contents), "for mgmt", len(mgmt_contents)
             print "file is malformed or the order of input folders is wrong "
             continue

     #done with reading the binary blobs from file ; now check for timestamps are correct
         '''
         if  (data_file_current_timestamp < t1-1):
             continue
         if (data_file_current_timestamp >t2+1):
             break
         '''
         data_packet_sizes_per_min, mgmt_packet_sizes_per_min, ctrl_packet_sizes_per_min=[],[],[]
         err_data_packet_sizes_per_min, err_mgmt_packet_sizes_per_min, err_ctrl_packet_sizes_per_min=[],[],[]
 
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
             if success:
                 for key in frame_elem.keys():
                     tsf=key
                 parse_data_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 if radiotap_len ==RADIOTAP_TX_LEN :
                     #datakind,tx,non-corrupted,src mac,dest mac,packetsize,bitrate,retranmission
                     if 1: #write this condition 
                         data_packet_sizes_per_min.append([1,1,0,temp[11],temp[12],temp[-1], temp[3],0])
                     else:
                         data_packet_sizes_per_min.append([1,1,0,temp[11],temp[12],temp[-1], temp[3],-1])
                 elif radiotap_len==RADIOTAP_RX_LEN :
                     #datakind,rx,non-corrupted,src mac,dest mac,packetsize,bitrate,retranmission
                     data_packet_sizes_per_min.append([1,0,0,temp[12],temp[13],temp[10], temp[8],-2])
                 else:
                     print "impossible ratdiotap detected ; Report CERN"
                     damaged_frame +=1 
#TODO: add the retransmissions count 
             else:
                print "success denied; incorrect data frame"
                damaged_frames +=1
             data_index=data_index+DATA_STRUCT_SIZE
             del frame_elem
             del monitor_elem

         data_index=0
         for idx in xrange(0,len(err_data_frames)-DATA_ERR_STRUCT_SIZE,DATA_ERR_STRUCT_SIZE):	
             frame=err_data_frames[data_index:data_index+DATA_ERR_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem=defaultdict(list)
             monitor_elem=defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success:
                 for key in frame_elem.keys():
                     tsf=key
                 parse_err_data_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 if radiotap_len == RADIOTAP_RX_LEN:
                     #datakind,tx,non-corrupted,packetsize,bitrate
                     err_data_packet_sizes_per_min.append([1,1,1,temp[10], temp[8]])
                 elif radiotap_len ==RADIOTAP_TX_LEN :
                     print "MGMT TX ERR !CALL CERN!"
                 else :
                    print "impossible radiotap len detected ; Report CERN"
                    damaged_frame +=1 
             else :
                 print "success denied; incorrect data frame"
                 damaged_frames +=1
             data_index= data_index+DATA_ERR_STRUCT_SIZE
             del frame_elem
             del monitor_elem

         beacon_mgmt_frames=header_and_beacon_mgmt_frames[mgmt_file_header_byte_count+1:]
         mgmt_index=0
         for idx in xrange(0,len(beacon_mgmt_frames)-MGMT_BEACON_STRUCT_SIZE ,MGMT_BEACON_STRUCT_SIZE ):
             frame=beacon_mgmt_frames[mgmt_index:mgmt_index+MGMT_BEACON_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem,monitor_elem=defaultdict(list),defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             if not( radiotap_len ==RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                 print "the radiotap header is not correct "
                 sys.exit(1)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success :
                 for key in frame_elem.keys():
                     tsf=key
                 parse_mgmt_beacon_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 if radiotap_len == RADIOTAP_TX_LEN:
                     print "beacon transmitted by AP !" 
                     print temp
                     sys.exit(1)
                 elif radiotap_len ==RADIOTAP_RX_LEN :
                     #mgmtkind, rx,non-corrupted,src_mac,bitrate,packet_size
                     mgmt_packet_sizes_per_min.append([2,0,0,temp[12],temp[8],temp[10]])
                 else :
                    print "impossible radiotap len detected ; Report CERN"
             else :
                 print "success denied"
             mgmt_index=mgmt_index+MGMT_BEACON_STRUCT_SIZE
             del frame_elem
             del monitor_elem

         mgmt_index=0
         for idx in xrange(0,len(common_mgmt_frames)-MGMT_COMMON_STRUCT_SIZE,MGMT_COMMON_STRUCT_SIZE ):
             frame=common_mgmt_frames[mgmt_index:mgmt_index+MGMT_COMMON_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem,monitor_elem=defaultdict(list),defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             if not( radiotap_len ==RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                 print "the radiotap header is not correct "
                 sys.exit(1)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success==1 :
                 for key in frame_elem.keys():
                     tsf=key
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 parse_mgmt_common_frame(frame,radiotap_len,frame_elem)
                 if radiotap_len == RADIOTAP_TX_LEN:
                     mgmt_packet_sizes_per_min.append([2,0,0,temp[12],temp[8],temp[10]]) #mgmt probe responses
                 elif radiotap_len ==RADIOTAP_RX_LEN :
                     #mgmt kind,rx,corrupted,src,bitrate,pktsize
                     mgmt_packet_sizes_per_min.append([2,0,0,temp[12],temp[8],temp[10]])
                 else :
                     print "impossible radiotap detected"
             else :
                 print "common mgmt success denied"
             mgmt_index= mgmt_index+MGMT_COMMON_STRUCT_SIZE
             del frame_elem
             del monitor_elem

         mgmt_index=0
         for idx in xrange(0,len(err_mgmt_frames)-MGMT_ERR_STRUCT_SIZE,MGMT_ERR_STRUCT_SIZE ):
             frame=err_mgmt_frames[mgmt_index:mgmt_index+MGMT_ERR_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem,monitor_elem=defaultdict(list),defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             if not( radiotap_len ==RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                 print "the radiotap header is not correct "
                 sys.exit(1)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success==1 :
                 for key in frame_elem.keys():
                     tsf=key
                 parse_mgmt_err_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 if radiotap_len == RADIOTAP_TX_LEN:
                     print "MGMT TX ERR !CALL CERN!"
                 elif radiotap_len ==RADIOTAP_RX_LEN :
                     #mgmt kind,rx,corrupted,src,bitrate,pktsize
                     err_mgmt_packet_sizes_per_min.append([2,0,1,temp[8],temp[10]])
                 else :
                     print "impossible radiotap detected"
             else:
                 print "success denied"
             mgmt_index= mgmt_index+MGMT_ERR_STRUCT_SIZE
             del frame_elem
             del monitor_elem

        #print "----------done with missed .. now with actual ctrl data "

         correct_ctrl_frames=header_and_correct_ctrl_frames[ctrl_file_header_byte_count+1:]
         ctrl_index=0
         for idx in xrange(0,len(correct_ctrl_frames)-CTRL_STRUCT_SIZE ,CTRL_STRUCT_SIZE ):
             frame=correct_ctrl_frames[ctrl_index:ctrl_index+CTRL_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem, monitor_elem=defaultdict(list),defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             if not( radiotap_len ==RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                 print "the radiotap header is not correct "
                 sys.exit(1)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success :
                 for key in frame_elem.keys():
                     tsf=key
                 parse_ctrl_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf]
                 temp.insert(0,tsf)
                 if radiotap_len ==RADIOTAP_TX_LEN : 
                     #print temp
                     #print "CTRL frame in TX ; call CERN? "
                     pass
                 elif radiotap_len==RADIOTAP_RX_LEN :
                     #ctrlkind,rx,src mac,dest mac,packetsize,bitrate,retranmission
                     print temp
                     ctrl_packet_sizes_per_min.append([3,0,0,temp[-2],temp[8],temp[10],temp[12][1]])
             else :
                 print "success denied"
             ctrl_index=ctrl_index+CTRL_STRUCT_SIZE
             del frame_elem
             del monitor_elem

         ctrl_index=0
         for idx in xrange(0,len(err_ctrl_frames)-CTRL_ERR_STRUCT_SIZE,CTRL_ERR_STRUCT_SIZE):	
             frame=err_ctrl_frames[ctrl_index:ctrl_index+CTRL_ERR_STRUCT_SIZE]
             offset,success,tsf= 8,-1,0
             header = frame[:offset]
             frame_elem,monitor_elem=defaultdict(list),defaultdict(list)
             (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
             if not( radiotap_len ==RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                 print "the radiotap header is not correct "
                 sys.exit(1)
             (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
             if success ==1:
                 for key in frame_elem.keys():
                     tsf=key
                 parse_ctrl_err_frame(frame,radiotap_len,frame_elem)
                 temp=frame_elem[tsf] 
                 temp.insert(0,tsf)
                 if radiotap_len ==RADIOTAP_TX_LEN :
                    print "ctrl frame transmitted; call CERN!" 
                    err_ctrl_packet_sizes_per_min.append([rate,size])
                 elif radiotap_len==RADIOTAP_RX_LEN :
                    #ctrlkind,rx,err,mac-add,bitrate, packet_size
                    err_ctrl_packet_sizes_per_min.append([3,0,1,temp[8],temp[10]])
             else :
                 print "success denied"
             ctrl_index= ctrl_index+CTRL_ERR_STRUCT_SIZE
             del frame_elem
             del monitor_elem
                      
         if file_count %10 == 0:
             print file_count

def queue_dynamics_plotter(router_id,output_folder):
    '''
    Plots the maximum size of the queue with time for a whole day.
    '''
#TODO: Fix it to plot queue dynamics per queue type ! Totally forgot to
#disect the graphs this way ! meh
    timeseries_mpdu,timeseries_ampdu,mpdu_list,ampdu_list=[],[],[],[]
    mpdu_dynamics_timestamp=mpdu_dynamics.keys()
    ampdu_dynamics_timestamp=ampdu_dynamics.keys()
    mpdu_dynamics_timestamp.sort()
    ampdu_dynamics_timestamp.sort()
    for timestamp in mpdu_dynamics_timestamp:
         timeseries_mpdu.append(timestamp), mpdu_list.append(max(mpdu_dynamics[timestamp]))

    for timestamp in ampdu_dynamics_timestamp:
         timeseries_ampdu.append(timestamp), ampdu_list.append(max(ampdu_dynamics[timestamp]))

    plot_timeseries(timeseries_ampdu,ampdu_list, timeseries_mpdu, mpdu_list,
                    'time',
                    'max MPDU queue per minute',
                    'max AMPDU queue per minute',
                    'Variation of Queue length with time',
                    output_folder+router_id+'_Qlen_.png', router_id)
    print "damage frame count " , damaged_frames


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
    print "now processing the files to calculate time "
    #for plotting traffic transmitted from each queue
    #per_queue_classification(t1,t2,data_fs)
    #for plotting queue sizes with time
    #queue_file_reader(t1,t2,data_fs)
    #queue_dynamics_plotter(router_id,output_folder)
    total_file_content_reader(t1,t2,data_fs,data_f_dir)
