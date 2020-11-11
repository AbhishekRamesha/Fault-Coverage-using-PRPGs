# Python 3.7.2 (v3.7.2:9a3ffc0492, Dec 24 2018, 02:44:43) 
# [Clang 6.0 (clang-600.0.57)] on darwin
# Type "help", "copyright", "credits" or "license()" for more information.
# >>> # Class used to store information for a wire
import csv
class Node(object):
    def __init__(self, name, value, gatetype, fcirc_innames):
        self.name = name         # string
        self.value = value        # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype    # string such as "AND", "OR" etc
        #self.interms = []     # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        #self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False    # boolean: true if this wire is a primary input of the circuit
        self.is_output = False   # boolean: true if this wire is a primary output of the circuit
        self.gate_input = False # True if this wire is a gate input
        self.gate_output = False #True if the wire is a gate output
        self.fcirc_interms = [] #list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.fcirc_innames = fcirc_innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them

    def set_value(self, v):
        self.value = v 

    def faultdisplay(self): # print out the node nicely on one line  
        if self.is_input: 
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}" 
            print(nodeinfo)
            return 
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
            interm_str = " "
            interm_val_str = " "
            for i in self.fcirc_interms:
                interm_str += str(i.name)+" "
                interm_val_str += str(i.value)+" "
            nodeinfo += f"as {self.gatetype:>5}"
            nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"
        elif self.gate_input:
          nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"
          interm_str = " "
          for i in self.fcirc_interms:
            interm_str += str(i.name)+" "
            nodeinfo += f"as {self.gatetype:>5}"
            nodeinfo += f"  of   {interm_str:20} "
        else:# internal nodes   
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"
            interm_str = " "
            interm_val_str = " "
            for i in self.fcirc_interms:
                interm_str += str(i.name)+" "
                interm_val_str += str(i.value)+" "

            nodeinfo += f"as {self.gatetype:>5}"
            nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"
        print(nodeinfo)
        return     

    # calculates the value of a node based on 
    #its gate type and values at interm
    def fcalculate_value(self):
        TheUcase = 0
        The1case = 0
        The0case = 0
        
        if self.gatetype == "AND":
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value== "1":
                    The1case +=1
                if The0case >0:
                    fval = "0" 
                if TheUcase ==0 and The0case ==0: # 11
                    fval = "1" 
                if The1case !=0 and TheUcase !=0: # 1U/U1
                    fval = "U" 
                if The1case ==0 and The0case ==0: # UU 
                    fval = "U"             
            self.value = fval
            return fval
        elif self.gatetype == "Equal":
            for i in self.fcirc_interms:
                if i.value == "U":
                    fval = "U"
                if i.value == "0":
                    fval = "0"
                if i.value== "1":
                    fval = "1"
            self.value = fval
            return fval   
        elif self.gatetype == "OR":
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value == "1":
                    The1case +=1        
                if The1case >0:
                    fval = "1"
                if TheUcase ==0 and The1case==0: #00
                    fval = "0"
                #if The1case ==0 and TheUcase!=0: #0U CASE
                    #val = "U"  
                if The0case !=0 and TheUcase!=0: #U0/0U
                    fval = "U"    
                if The0case ==0 and The1case==0: #UU
                    fval ="U"       
            self.value = fval
            return fval
        elif self.gatetype == "NAND":
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value == "1":
                    The1case +=1        
                if The0case >0:
                    fval = "1"
                if TheUcase == 0 and The0case ==0: #11
                    fval = "0"     
                if The1case !=0 and TheUcase !=0: #1U/U1
                    fval = "U" 
                if The1case ==0 and The0case ==0:#UU
                    fval = "U"      
            self.value = fval
            return fval
        elif self.gatetype == "NOT":
            for i in self.fcirc_interms:
                if i.value == "0":
                    fval= "1"
                elif i.value=="1":
                    fval="0"
                elif i.value == "U":
                    fval="U"
            self.value = fval
            return fval     
        elif self.gatetype == "XOR":
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value == "1":
                    The1case +=1        
                if TheUcase >0: #FOR ANY INPUT U
                    fval = "U"
                if The0case ==0 and TheUcase ==0: #11 
                    fval = "0"
                if The1case ==0 and TheUcase ==0: #00
                    fval = "0" 
                if The0case !=0 and The1case !=0: #01
                    fval = "1"                  
            self.value = fval
            return fval
        elif self.gatetype == "XNOR":
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value == "1":
                    The1case +=1        
                if TheUcase >0: #FOR ANY INPUT U
                    fval = "U"
                if The0case ==0 and TheUcase ==0: #11 
                    fval = "1"
                if The1case ==0 and TheUcase ==0: #00 
                    fval = "1" 
                if The0case !=0 and The1case !=0: #01 
                    fval = "0" 
            self.value = fval
            return fval           
        elif self.gatetype == "NOR":
            fval = "1"
            for i in self.fcirc_interms:
                if i.value == "U":
                    TheUcase +=1
                if i.value == "0":
                    The0case +=1
                if i.value == "1":
                    The1case +=1        
                if The1case >0:
                    fval = "0"
                if The1case ==0 and TheUcase==0: #00
                    fval = "1"
                if The1case ==0 and The0case==0: #UU
                    fval = "U"    
                if The0case !=0 and TheUcase!=0: #0U/U0
                    fval = "U"                    
            self.value = fval
            return fval
        elif self.gatetype == "BUFF":
            fval = self.fcirc_interms[0].value
            self.value = fval
            return fval            
  
# Take a line from the circuit file which represents a gatetype operation and returns a node that stores the gatetype
def parse_gate(rawline):
# example rawline is: a' = NAND(b', 256, c')
# should return: node_name = a',  node_gatetype = NAND,  node_innames = [b', 256, c']
    # get rid of all spaces
    line = rawline.replace(" ", "")
    # now line = a'=NAND(b',256,c')

    name_end_idx = line.find("=")
    node_name = line[0:name_end_idx]
    # now node_name = a'

    gt_start_idx = line.find("=") + 1
    gt_end_idx = line.find("(")
    node_gatetype = line[gt_start_idx:gt_end_idx]
    # now node_gatetype = NAND

    # get the string of interms between ( ) to build tp_list
    interm_start_idx = line.find("(") + 1
    end_position = line.find(")")
    temp_str = line[interm_start_idx:end_position]
    tp_list = temp_str.split(",")
    # now tp_list = [b', 256, c]
  
    #node_innames = [i for i in tp_list]
    #now node_innames = [b', 256, c]
    fnode_innames = [i for i in tp_list]
    return node_name, node_gatetype, fnode_innames

# Create circuit node list from input file
def construct_nodelist():
    o_name_list = []

    for line in input_file_values:
        if line == "\n":
            continue

        if line.startswith("#"):
            continue

        # TODO: clean this up
        if line.startswith("INPUT"):
            index = line.find(")")
            # intValue = str(line[6:index])
            name = str(line[6:index])
            n = Node(name, "U", "PI", [])
            n.is_input = True
            #node_list.append(n)
            Fault_list.append(n)

        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)

        else:  # majority of internal gates processed here
            node_name, node_gatetype, fnode_innames = parse_gate(line)
            p= Node(node_name, "U", node_gatetype, fnode_innames)
            p.gate_output = True
            for i in range(len(p.fcirc_innames)):
              #v=node.name
              w= str(p.fcirc_innames[i])
              p.fcirc_innames[i] = p.name +"-"+p.fcirc_innames[i]
              r = p.fcirc_innames[i]
              #inputof = node.name        
              n = Node(r, "U", "Equal",w)  
              n.gate_input = True
              Fault_list.append(n)  
            Fault_list.append(p)
    #for node in Fault_list:
      #print(node.fcirc_innames)
    for n in Fault_list:
        if n.name in o_name_list:
            n.is_output = True

    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    
    for node in Fault_list:
        node.fcirc_innames = [node.fcirc_innames] if isinstance(node.fcirc_innames, str) else node.fcirc_innames
        for cur_name in node.fcirc_innames:
            for target_node in Fault_list:
                if target_node.name == str(cur_name):
                    node.fcirc_interms.append(target_node)
     
    #for node in Fault_list:
      #print(node.fcirc_interms)

    return 

def cloning(node_list):
    newFault_list = []
    newFault_list.extend(node_list) #extend takes 0.05 seconds , cloning take 0.075 seconds
    return newFault_list

def fault_list():
    for node in Fault_list:
      if node.is_input:
        all_Faults.append(node.name + "-0")
        all_Faults.append(node.name + "-1")

      else:
        all_Faults.append(node.name + "-0")
        all_Faults.append(node.name + "-1")
    return

def generate_binary(n):
    a = []
    global bin_arr
    bin_arr = []
    #z = 2**n
    if n < 7:
      for i in range(2**n):
          line = [i//2**j%2 for j in reversed(range(n))]
          a.append(line)
    else:
      for x in range(100):
          line = [x//2**j%2 for j in reversed(range(n))]
          a.append(line) 

    for i in range(len(a)):
      temp_input_list = a[i]
      #print(temp_input_list)
      bin_arr.append(''.join(str(i) for i in temp_input_list))

    return bin_arr

def hextobin(seed):
  hexadecimal = seed
  end_length = len(hexadecimal) * 4

  hex_as_int = int(hexadecimal, 16)
  hex_as_binary = bin(hex_as_int)
  padded_binary = hex_as_binary[2:].zfill(end_length)

  #print(padded_binary)
  return padded_binary
    

def add_binary_nums(x,y):
        max_len = max(len(x), len(y))
        x = x.zfill(max_len)
        y = y.zfill(max_len)
        result = ''
        carry = 0
        for i in range(max_len-1, -1, -1):
            r = carry
            r += 1 if x[i] == '1' else 0
            r += 1 if y[i] == '1' else 0
            result = ('1' if r % 2 == 1 else '0') + result
            carry = 0 if r < 2 else 1       
        if carry !=0 : result = '1' + result
        return result.zfill(max_len)

def counter(binseed,inputlen,inputspace,fixtvsize):
  global countertv_list
  if inputspace<fixtvsize:
    countertv_list = range (0,inputspace)
  else:
    countertv_list = range (0, fixtvsize)

  binseed = binseed[:inputlen]
  one = str(1)
  countertv_list = [binseed for i in countertv_list]
  
  for i in range(len(countertv_list)-1):
    binseed = add_binary_nums(binseed,one)
    #binseed = bin(int(binseed,2) + int(one,2))
    countertv_list[i+1] = binseed

  return countertv_list  

def Convert(string): 
    li = list(string) 
    return li 
def listToString(s):  
    #initialize an empty string 
    str1 = ""  
    # traverse in the string   
    for ele in s:  
        str1 += ele   
    # return string   
    return str1        
def lfsr(seed, taps):
    a = []
    sr = []
    srnew = []
    sr = Convert(seed)
    a.append(seed)
    #print (sr[0])
    while srnew != seed:
        srnew = Convert(sr)
        for t in taps:
          if t > (len(sr)-1):
            continue
          else:  
            srnew[t] = str(int(sr[t-1]) ^ int(sr[7]))
        
        for r in range(0,len(srnew)):
          if r in taps:
            continue
          elif r==0:
            (srnew[r]) = str(sr[7])
          else:
            (srnew[r]) = str(sr[r-1]) 

        sr = srnew
        srstr = listToString(srnew)     

        a.append(srstr)
        if len(a) == 100:
            break
    return a
#print(lfsr('11001000', (2,4,5)))

def LFSR1(binseed,taps,inputlen,inputspace,fixtvsize):
  global LFSR1tv_list
  if inputspace<fixtvsize:
    LFSR1tv_list = range (0,inputspace)
  else:
    LFSR1tv_list = range (0, fixtvsize)
  
  divseed = []
  if inputlen > 8:
    #The following piece of code till the end of while loop is to concatenate the given hexadecimal seed and make it larger just in case it is not sufficient for a large bench 
     moreseed = len(binseed)-4
     while inputlen > moreseed:
       binseed+=binseed
       moreseed = len(binseed)
       suffseed = moreseed % 8
       moreseed -= suffseed
    # Slice seed to form 8-bit seeds for lfsrs
     completelfsr = inputlen // 8
     partiallfsr = inputlen % 8
     if partiallfsr == 0:
        lfsrsize = completelfsr
     else:
        lfsrsize = completelfsr + 1
     #divseed = range(0, lfsrsize)
     a= 0
     b= 8
     tempcount = 0
     while tempcount != lfsrsize:
        #divseed = [binseed[a:b] for i in divseed]
        tempdivseed = binseed[a:b]
        divseed.append(tempdivseed)
        a +=8
        b +=8
        tempcount+=1  
  else:
    lfsrsize = 1
    divseed = range(0, lfsrsize)
    divseed = [binseed[0:8] for i in divseed]  
  print (divseed)  
 
  temptvlist = []
  count = 0
  for i in range (len(divseed)):
    LFSR1output = []
    LFSR1output = lfsr(divseed[i],taps)
    if count == 0: 
        #for v in range (0,len(LFSR1output)):
       temptvlist.extend(LFSR1output)
    else:
      minperiod = min(len(temptvlist),len(LFSR1output))
      for v in range (0,minperiod):  
        temptvlist[v]+=LFSR1output[v]
    count+=1  
  
  for i in range(len(temptvlist)):
    temptvlist[i] = temptvlist[i][:inputlen]
  if inputspace<fixtvsize:   
    temptvlist = temptvlist [:inputspace] 
  else:
    temptvlist = temptvlist [:fixtvsize]   
  LFSR1tv_list = temptvlist 
  return LFSR1tv_list

   
# Main function starts
# Step 1: get circuit file name from command line
wantToInputCircuitFile = str(
    input("Provide a benchfile name (return to accept circuit.bench by default):\n"))

if len(wantToInputCircuitFile) != 0:
    circuitFile = wantToInputCircuitFile
    try:
        f = open(circuitFile)
        f.close()
    except FileNotFoundError:
        print('File does not exist, setting circuit file to default')
        circuitFile = "circuit.bench"
else:
    circuitFile = "circuit.bench"

# Constructing the circuit netlist
file1 = open(circuitFile, "r")
input_file_values = file1.readlines()
file1.close()
Fault_list = []
construct_nodelist()
all_Faults = []
fault_list()
Testvector_list = []

#printing list of constructed nodes
#print("\nCircuit node list:")
#for n in Fault_list:
    #n.faultdisplay()

print ("----------------------------------------------")

print("\nFull fault list without repetition for the given circuit bench is as follows:")
print (all_Faults)
print ("\nThere are a total of " + str(len(all_Faults))+ " faults in the given circuit bench") 

print ("----------------------------------------------")

inputlen = 0   
for node in Fault_list:
   if node.is_input:
     inputlen +=1

PRPG = str(input("\nWhich PRPG do you want to use?:\nType:\n'none' for small circuits with inputs less than 7\n'counter' for n-bit counter generated test vectors for a circuit with inputs greater than or equal to 7\n'LFSR' for 8-bit LFSR for a circuit with inputs greater than or equal to 7\n"))

inputspace = 2**inputlen
fixtvsize = 100

if PRPG == "none":
  generate_binary(inputlen)
  if inputspace<fixtvsize:
    Testvector_list = bin_arr
  else:
    #Testvector_list = random.sample(bin_arr,fixtvsize)
    Testvector_list = bin_arr 
elif PRPG == "counter":
  Seed = input("Enter your choice of Seed in hexadecimal format:\n")
  Binseed = hextobin(Seed)
  counter(Binseed,inputlen,inputspace,fixtvsize)
  Testvector_list = countertv_list   
elif PRPG == "LFSR":
  Seed = input("Enter your choice of Seed in hexadecimal format:\n")
  Binseed = hextobin(Seed)
  tap = input("Enter the tap Configuartion:\nType:\n10000000 for no taps\n10101100 for taps at 2,4,5\n10111000 for taps at 2,3,4\n10010101 for taps at 3,5,7\n")
  if tap == "10000000":
    taps = []
    LFSR1(Binseed,taps,inputlen,inputspace,fixtvsize)
    Testvector_list = LFSR1tv_list 
  elif tap == "10101100":
    taps = [2,4,5]
    LFSR1(Binseed,taps,inputlen,inputspace,fixtvsize)
    Testvector_list = LFSR1tv_list
  elif tap == "10111000":
    taps = [2,3,4]
    LFSR1(Binseed,taps,inputlen,inputspace,fixtvsize)
    Testvector_list = LFSR1tv_list
  elif tap == "10010101":
    taps = [3,5,7]
    LFSR1(Binseed,taps,inputlen,inputspace,fixtvsize)
    Testvector_list = LFSR1tv_list     

b_yesno = str(input("\nDo you want to proceed to see the fault coverage of each test vector?(Type yes or no)\n"))

if b_yesno=="yes":   
  #generate_binary(inputlen)
  with open("circuit_all.csv", "w+") as csvfile:
    print("\nThere are " + str(len(Testvector_list)) + " possible test vectors for given circuit bench:")
    print (Testvector_list)
    print ("----------------------------------------------")

    print("\nThe fault coverage of each of these " + str(len(Testvector_list)) + " Test Vectors is as follows:")

    for p in range(len(Testvector_list)):
      old_list = [] # good circuit output for a test vector 
      new_list = [] # bad circuit output for a test vector and a fault
      undetected_fault = [] # all faults undetected by a test vector
      detected_fault = [] # all faults detected by a test vector

      #clear all good circuit nodes
      for node in Fault_list:
        node.set_value("U")
   
      line_of_val = Testvector_list[p]
      if len(line_of_val)==0:
         break

      strindex = 0
          # Set value of good circuit input nodes
      for node in Fault_list:
          if node.is_input:
              if strindex > len(line_of_val)-1:
                  break
              node.set_value(line_of_val[strindex])
              strindex = strindex + 1 
   
      # simulation by trying calculating each node's value in the list
      updated_count = 1 #initialize to 1 to enter while loop at least once
      iteration = 0
      while updated_count > 0:
          updated_count = 0
          iteration += 1
          for n in Fault_list:
              if n.value == "U":
                  n.fcalculate_value()
                  if n.value == "0" or n.value == "1":
                      updated_count +=1
              #n.faultdisplay()
        
      #print("\n--- Good circuit Simulation results: ---")
      input_list = [i.name for i in Fault_list if i.is_input]
      input_val = [i.value for i in Fault_list if i.is_input]
      #print("input: \t", end="")
      #print(*input_list, end = "")
      #print("\t = \t", end = "")
      #print(*input_val)
      output_list = [i.name for i in Fault_list if i.is_output]
      output_val = [i.value for i in Fault_list if i.is_output]
      old_list = cloning(output_val)
      #old_list.append(output_val)

      #newFault_list = cloning(Fault_list)
      for i in range (len(Fault_list)):
          faultcount = 0
          while faultcount< 2:
              for node in Fault_list:
                  node.set_value("U")
              strindex = 0
              for node in Fault_list:
                  if node.is_input:
                      if strindex > len(line_of_val)-1:
                          break
                      node.set_value(line_of_val[strindex])
                      strindex = strindex + 1
                  #node.faultdisplay()
            
              x = Fault_list [i]
              x.value = str(faultcount)

              for node in Fault_list:
                  if node.value == "U":
                     node.fcalculate_value()
                  #node.faultdisplay()
        
              fault_input_list = [i.name for i in Fault_list if i.is_input]
              fault_input_val = [i.value for i in Fault_list if i.is_input]
              #print("\n\ninput: \t", end="")
              #print(*fault_input_list, end = "")
              #print("\t = \t", end = "")
              #print(*fault_input_val)
              fault_output_list = [i.name for i in Fault_list if i.is_output]
              fault_output_val = [i.value for i in Fault_list if i.is_output]
              new_list = cloning(fault_output_val)
              #new_list.append(fault_output_val)
              #print("output:\t", end="")
              #print(*fault_output_list, end = "")
              #print("\t = \t", end = "")
              #print(*fault_output_val)

              if old_list == new_list:
                undetected_fault.append(Fault_list[i].name + "-" + str(Fault_list[i].value))
              else:
                detected_fault.append(Fault_list[i].name + "-" + str(Fault_list[i].value))

              faultcount += 1
      print (Testvector_list[p], end ="")
      print (":", end="")
      print (*detected_fault, sep = ",")
      print("The test vector " + Testvector_list[p] + " detectes " + str(len(detected_fault)) + " faults")

      writer = csv.writer(csvfile)
      writer.writerow([Testvector_list[p], *detected_fault])
  csvfile.close()
print ("----------------------------------------------")

c_yesno = str(input("\nDo you want to proceed to see the fault coverage of a list of test vectors in order?(Type yes or no)\n"))

if c_yesno=="yes":   
  print("\nGiven following test vector list:")
  print(Testvector_list)
  print("\nThe fault coverage of the  " + str(len(Testvector_list)) + " Test Vectors in order is as follows:")
  alldrep = [] # all faults detected by all tvs with repetition
  alldetected = [] # all faults detected by all tvs without rep. 'D'
  count_plot = 1
  per_plot_list = []
  plot_list = []
  with open("circuit_list.csv", "w+") as file:
    for p in range(len(Testvector_list)):
    #for p in reversed(range(len(Testvector_list))):
      goodoutput_list = [] 
      badoutput_list = []
      undetected_fault = [] #faults not detetected by current tv
      detected_fault = [] # faults detected by current tv with repetition
      resultantlist = [] # faults detected by current tv without repetition

      if len(alldetected) == 0:
        print("\nApplying " + Testvector_list[p] + " to the remaining " +str(len(all_Faults)) + " faults:")
        print(*all_Faults, sep = ",")
      else:
        for item in all_Faults:
          if item not in alldetected:
            undetected_fault.append(item)
        print("\nApplying " + Testvector_list[p] + " to the remaining " +str(len(undetected_fault)) + " faults:")
        print(*undetected_fault, sep = ",")

      #clear all good circuit nodes
      for node in Fault_list:
        node.set_value("U")
   
      line_of_val = Testvector_list[p]
      if len(line_of_val)==0:
         break

      strindex = 0
       # Set value of good circuit input nodes
      for node in Fault_list:
       if node.is_input:
           if strindex > len(line_of_val)-1:
                break
           node.set_value(line_of_val[strindex])
           strindex = strindex + 1 
           
      # simulation by trying calculating each node's value in the list
      updated_count = 1 #initialize to 1 to enter while loop at least once
      iteration = 0
      while updated_count > 0:
        updated_count = 0
        iteration += 1
        for n in Fault_list:
            if n.value == "U":
                n.fcalculate_value()
                if n.value == "0" or n.value == "1":
                    updated_count +=1
            #n.faultdisplay()

      #for node in Fault_list:
        #if node.value == "U":
            #node.fcalculate_value()
        #node.faultdisplay()         
        
      #print("\n--- Good circuit Simulation results: ---")
      input_list = [i.name for i in Fault_list if i.is_input]
      input_val = [i.value for i in Fault_list if i.is_input]

      #print("input: \t", end="")
      #print(*input_list, end = "")
      #print("\t = \t", end = "")
      #print(*input_val)

      output_list = [i.name for i in Fault_list if i.is_output]
      output_val = [i.value for i in Fault_list if i.is_output]
      goodoutput_list = [*output_val]

      newFault_list = cloning(Fault_list)
      for i in range (len(newFault_list)):
       faultcount = 0
       while faultcount< 2:
            for node in newFault_list:
                node.set_value("U")
            strindex = 0
            for node in newFault_list:
                if node.is_input:
                    if strindex > len(line_of_val)-1:
                        break
                    node.set_value(line_of_val[strindex])
                    strindex = strindex + 1
                #node.faultdisplay()
          
            x = newFault_list [i]
            x.value = str(faultcount)
            for node in newFault_list:
                  if node.value == "U":
                     node.fcalculate_value()
                  #node.faultdisplay()
        
            fault_input_list = [i.name for i in newFault_list if i.is_input]
            fault_input_val = [i.value for i in newFault_list if i.is_input]

            #print("\n\ninput: \t", end="")
            #print(*fault_input_list, end = "")
            #print("\t = \t", end = "")
            #print(*fault_input_val)

            fault_output_list = [i.name for i in newFault_list if i.is_output]
            fault_output_val = [i.value for i in newFault_list if i.is_output]
            badoutput_list = [*fault_output_val]
    
            #print("output:\t", end="")
            #print(*fault_output_list, end = "")
            #print("\t = \t", end = "")
            #print(*fault_output_val)


            if goodoutput_list == badoutput_list:
                #undetected_fault.append(Fault_list[i].name + "-" + str(Fault_list[i].value))
                pass
            else:
                detected_fault.append(newFault_list[i].name + "-" + str(newFault_list[i].value))

            faultcount += 1
   
      #resultantlist = m - detected_fault
      for item in detected_fault:
        if item not in alldrep:
          resultantlist.append(item)

      print("The test vector " + Testvector_list[p] + " detectes " + str(len(resultantlist)) + " faults")
                 
      print (Testvector_list[p], end ="")
      print (":", end="")
      print (*resultantlist, sep = ",")

      csvwriter = csv.writer(file)
      csvwriter.writerow([Testvector_list[p], *resultantlist])

      alldrep.extend(detected_fault)
      alldetected.extend(resultantlist) 

      if p%10 == 0:
        per1 = len(alldetected)
        per2 = len(all_Faults)
        per_plot = (per1/per2)*100
        plot_list.append(per_plot)

print(plot_list)
filename = "plot_1355_per.csv"
with open(filename, 'a') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)  
    #csvwriter.writerow(input_per_list)    
    # writing the fields  
    csvwriter.writerow(plot_list)


print(f"Finished - bye!")
