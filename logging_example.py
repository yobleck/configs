import sys
from datetime import datetime;
#logging module may also be useful
cwd = sys.path[0];

def my_func(var):
    print(var);

logging = True;
if(logging):
    log = open(cwd + "/log.txt","a");log.write("\n" + str(datetime.now().isoformat()) + " LOGGING STARTED\n");log.close();
    def logger(func):
        def inner(*args, **kwargs):
            log = open(cwd + "/log.txt","a");
            log.write(str(datetime.now().isoformat())+" func: "+str(func.__qualname__)+" *args: "+str(args)+" **kwargs: "+str(kwargs)+"\n");
            log.close();
            return func(*args, **kwargs);
        return inner; 
    
    #my_func = logger(my_func);
    print = logger(print);

#my_func("test");
print("ddd", "DDD");
