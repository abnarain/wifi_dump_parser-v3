#Author : Abhinav Narain
#Date : 9-sept-2013
#Purpose : To plot the #devices,AP inside homes 

from magicplott import *

def pickle_reader(input_folder):
    print "the pickle reader called " 
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


if __name__=='__main__':    
    if len(sys.argv) !=3:
        print "usage : python unpickeler.py data_folder filename.png  "
        sys.exit(0)
    outfile_name = sys.argv[2]
    input_folder = sys.argv[1]
    if '.eps' not in outfile_name and '.png' not in outfile_name:
        print "Do you really want to write graph to %s?" % (outfile_name)
        sys.exit(0)
    [home_ap_table,home_device_table]=pickle_reader(input_folder)
    d= home_device_table
    new_list=[]
    for k,v in home_ap_table.iteritems():        
        list_devices=home_device_table[k]
        new_list_devices= [x for x in list_devices if x not in v]
        new_list.append([k,len(new_list_devices),len(v)])

    new_list.sort(key=lambda x: x[1])
    labels,home_device_count,home_ap_count=[],[],[]
    for i in new_list :
        labels.append(i[0])
        home_device_count.append(i[1])
        home_ap_count.append(i[2])
    bar_graph_plotter(labels,
                      home_device_count,
                      home_ap_count,
                      'RouterID',
                      'Device Count',
                      'Number of Devices and Access Points observed in homes(5 GHz)',
                      outfile_name
                      )

