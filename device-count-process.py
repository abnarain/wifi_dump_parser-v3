#Author : Abhinav Narain
#Date : Sept 8, 2013
#Purpose : To read the binary files with data from BISmark deployment in homes
import os,sys,re
import gzip
import struct 


from  header import *
from mac_parser import * 
from utils import *

try:
    import cPickle as pickle
except ImportError:
    import pickle

#List of corresponding files which were missing
missing_files=[]

#The unique set of devices seen in the time period
ap_macs,device_macs=set(), set()
#Rate map has the distribution of rates seen per minute
rate_map=defaultdict(list)
#device map has the list of devices seen per minute
device_map=defaultdict(list)
#ap map has the list of Access Points seen per minute
ap_map=defaultdict(list)

def file_reader() : 
    data_fs=os.listdir(data_f_dir)
    data_file_header_byte_count=0
    mgmt_file_header_byte_count=0
    file_timestamp=0
    file_counter=0 
    for data_f_name in data_fs :
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

        #done with reading the binary blobs from file ; now check for timestamps are correct
        if (not ( mgmt_file_current_timestamp == data_file_current_timestamp )) :
            print "timestamps don't match " 		
            sys.exit(1)
        else :
            file_timestamp=mgm_file_current_timestamp	
        if (not ( mgmt_file_seq_no == data_file_seq_no)):
            print "sequence number don't match "
            sys.exit(1)

        
        if ( len(data_contents) != 4 or len(mgmt_contents) !=6) :
            print "for data", len(data_contents), "for mgmt", len(mgmt_contents) 
            print "file is malformed or the order of input folders is wrong "
            continue 
        
        #The following code block parses the data file 	
        #print "----------done with missed .. now with actual data "
        correct_data_frames=header_and_correct_data_frames[data_file_header_byte_count+1:]
        data_index=0
        device_local_map=set()
        rate=[]
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
                    rate.append(frame_elem[tsf][7])
                    a= frame_elem[tsf][11].split(':')
                    if  not (a[0] =='ff' and a[1] =='ff' and a[2] =='ff' ):
                        if not (a[0] =='33' and a[1] =='33'  ) :
                            device_macs.add(frame_elem[tsf][11])
                            device_local_map.add(frame_elem[tsf][11])            
                    try:        
                        a= frame_elem[tsf][12].split(':')
                    except :
                        print "problem with mac element "
                        print frame_elem
                        continue
                    if  not (a[0] =='ff' and a[1] =='ff' and a[2] =='ff' ):
                        if not (a[0] =='33' and a[1] =='33'  ) :
                            device_macs.add(frame_elem[tsf][12])
                            device_local_map.add(frame_elem[tsf][12])
                elif radiotap_len ==RADIOTAP_TX_LEN :
                    rate.append(frame_elem[tsf][2])
            else:
                print "success denied"                    
            data_index=data_index+DATA_STRUCT_SIZE
            del frame_elem
            del monitor_elem
        device_map[file_timestamp]=device_local_map
        def histogram(L):
            d = {}
            for x in L:
                if x in d:
                    d[x] += 1
                else:
                    d[x] = 1
            return d
        rate_map[file_timestamp]= histogram(rate)
        rate=[]
        del device_local_map
        #The following code block parses the mgmt files 
        beacon_mgmt_frames=header_and_beacon_mgmt_frames[mgmt_file_header_byte_count+1:]
        mgmt_index=0
        ap_local_map=set()
        for idx in xrange(0,len(beacon_mgmt_frames)-MGMT_BEACON_STRUCT_SIZE ,MGMT_BEACON_STRUCT_SIZE ):		
            frame=beacon_mgmt_frames[mgmt_index:mgmt_index+MGMT_BEACON_STRUCT_SIZE]
            offset,success,tsf= 8,-1,0
            header = frame[:offset]
            frame_elem,monitor_elem=defaultdict(list),defaultdict(list)
            (version,pad,radiotap_len,present_flag)=struct.unpack('<BBHI',header)
            if not( radiotap_len == RADIOTAP_RX_LEN or  radiotap_len == RADIOTAP_TX_LEN) :
                print "the radiotap header is not correct "		
                sys.exit(1)
            (success,frame_elem,monitor_elem)=parse_radiotap(frame,radiotap_len,present_flag,offset,monitor_elem,frame_elem)
            if success :
                for key in frame_elem.keys():
                    tsf=key           
                parse_mgmt_beacon_frame(frame,radiotap_len,frame_elem)
                if radiotap_len== RADIOTAP_RX_LEN:
                    a= frame_elem[tsf][11].split(':')            
                    if  not (a[0] =='ff' and a[1] =='ff' and a[2] =='ff' ) :
                        if not (a[0] =='33' and a[1] =='33' ) :
                            ap_macs.add(frame_elem[tsf][11])
                            ap_local_map.add(frame_elem[tsf][11])
            else :
                print "success denied; beacon frames"        
            mgmt_index=mgmt_index+MGMT_BEACON_STRUCT_SIZE
            del frame_elem
            del monitor_elem

        ap_map[file_timestamp]=ap_local_map
        del ap_local_map
        #he following code block parses the ctrl files 

        file_counter +=1
        if file_counter %10 == 0:
            print file_counter
                
                
#not needed for phy errs

if __name__=='__main__':
    if len(sys.argv) !=5:	
	print len(sys.argv)
        print "Usage : python reader.py data/<data.gz> mgmt/<mgmt.gz>  <router_id> <o/p pickle> "
        sys.exit(1)
#compare regular expression for filenameif argv[1]

    data_f_dir=sys.argv[1]
    mgmt_f_dir=sys.argv[2]
    router_id=sys.argv[3]
    output_file=sys.argv[4]
    file_reader()
    print "mac address of devices "
    print len(device_macs)
    print "device macs "
    print len(device_map)
    print "mac address of aps"
    print len(ap_macs)
    print "==========="
    print len(ap_map)
    print "rate maps are " 
    print len(rate_map)
    print "done; writing to a file "
    global_list=[router_id,ap_macs,ap_map,device_macs,device_map,rate_map]
    output_device = open(output_file, 'wb')
    pickle.dump(global_list,output_device )
    output_device.close()
    print "finished writing files" 
    for i in range(0,len(missing_files)):
	print missing_files[i]
    print "number of files that can't be located ", len(missing_files)	
