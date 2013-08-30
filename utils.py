from collections import defaultdict
#from collections import Counter
import numpy as np
def median(mylist):
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]


def avg(sequence):
        if len(sequence) < 1: 
            return None
        else: 
            return sum(sequence) / len(sequence)   

def variance(sequence):
    def avg(sequence):
        if len(sequence) < 1: 
            return None
        else: 
            return sum(sequence) / len(sequence)   

    if len(sequence) < 1: 
        return None
    else:
        avg = avg(sequence)
        sdsq = sum([(i - avg) ** 2 for i in sequence])
        stdev = (sdsq / (len(sequence) - 1)) ** .5
        return stdev
        

#percentile is a real number (0,100)    
def percentile (sequence, percentile):
    if len(sequence) < 1: 
        value = None
    elif (percentile >= 100):
        sys.stderr.write('ERROR: percentile must be < 100.  you supplied: %s\n'% percentile)
        value = None
    else:
        element_idx = int(len(sequence) * (percentile / 100.0))
        sequence.sort()
        value = sequence[element_idx]
        return value

def mode(ls):
    a= list(map((lambda x: x * -1), ls))
    counts=np.bincount(a)
    return  -1* np.argmax(counts)
    '''
    b = Counter(ls)
    return b.most_common(1)
    max=-1
    modes =defaultdict(dict)

    for i in ls:
        modes[i]=ls.count(i)
    for i,k in modes.iteritems():
        if k >max :
            max=k
    for i,k in modes.iteritems():
        if k==max:
            return i
        '''
