#Author : Abhinav Narain
#Date : 5-sept-2013
#Purpose : To plot the devices inside homes 


from magicplott import *

'''
testing dataset :
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
def retx_map(_tx,_retx,threshold,router_id):
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


def pickle_reader(input_folder,threshold):
    print "the pickle reader called " 
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
        l=retx_map(transmission_count_table,retransmission_count_table,threshold,router_id)
        if len(l)==0:
            print router_id
            print len(l)
            undersampled_rate_list.append(router_id)
        else :
            retx_norm_table[router_id]=l

    return [c_table,retx_norm_table,undersampled_rate_list]	

if __name__=='__main__':    
    if len(sys.argv) !=3:
        print "usage : python unpickeler.py data_folder filename.png  "
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
        'Contention Delay(microsecond)',
                    0,
                    0,
                    'Scatterplot for retransmission vs Contention Delay in homes for 5GHz band',
                    outfile_name)
