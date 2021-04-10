import sys, random, time;

def run(timer=0.005, i_text=""):
    
    #parsing user time per random guess argument
    if(__name__ == "__main__"):
        if("-t" in sys.argv[1]):
            try:
                timer = float(sys.argv[1][3:]);
                sys.argv.pop(1);
            except Exception as e:
                print(str(e) + "\ntime argument must be formatted like \'-t=0.008\'\nand be the first argument");
                return -1;
        #else:
            #timer = 0.005;
    
    
    #getting and formatting input string
    if(__name__ == "__main__"):
        for x in sys.argv[1:]:
            i_text = i_text + " " + x;
        i_text = i_text[1:];
    
    #TODO: add regex to warn about non supported characters
    #TODO: remove previously checked chars from list to make timing more consistent
    
    #list of valid characters to choose from
    char_list = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[{]}|;:,<.>/? ";
    r_text = [];
    
    
    #convert list of char to string
    def l_to_s(l):
        s = "";
        for x in l:
            s += x;
        return s;
    
    
    print();
    while(len(r_text) < len(i_text)): #works its way up from no characters to input string len
        r_text.append( char_list[random.randint(0,len(char_list)-1)] );
        
        while(l_to_s(r_text) != i_text[:len(r_text)]): #trying and displaying random characters until they match the input
            print("\033[F" + l_to_s(r_text));
            time.sleep(timer); #to make output visible
            r_text[-1] = char_list[random.randint(0,len(char_list)-1)];

    print("\033[F" + l_to_s(r_text));


def list_of_char():
    print("list of acceptable characters:\n"+
          "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[{]}|;:,<.>/? "); #anti DRY I know


if __name__ == "__main__":
    run();
