import csv
import random
import itertools as it
#from math import comb
# Class used to store information for a wire
class Node(object):
    def __init__(self, name, value, gatetype, innames):
        self.name = name  # string
        self.value = value  # char: '0', '1', 'U' for unknown
        self.gatetype = gatetype  # string such as "AND", "OR" etc
        self.interms = []  # list of nodes (first as strings, then as nodes), each is a input wire to the gatetype
        self.innames = innames  # helper string to temperarily store the interms' names, useful to find all the interms nodes and link them
        self.is_input = False  # boolean: true if this wire is a primary input of the circuit
        self.is_output = False  # boolean: true if this wire is a primary output of the circuit
        self.is_fault = False  # boolean: true if the node is at fault

    def set_value(self, v):
        self.value = v

    def display(self):  # print out the node nicely on one line
        if self.is_input:
            nodeinfo = f"input:\t{str(self.name):5} = {self.value:^4}"
            print(nodeinfo)
            return
        elif self.is_output:
            nodeinfo = f"output:\t{str(self.name):5} = {self.value:^4}"
        else:  # internal nodes
            nodeinfo = f"wire:  \t{str(self.name):5} = {self.value:^4}"
        interm_str = " "
        interm_val_str = " "
        for i in self.interms:
            interm_str += str(i.name) + " "
            interm_val_str += str(i.value) + " "
        nodeinfo += f"as {self.gatetype:>5}"
        nodeinfo += f"  of   {interm_str:20} = {interm_val_str:20}"
        print(nodeinfo)
        return
        
   # calculates the value of a node based on its gate type and values at interms
    def calculate_value(self):
        if self.gatetype == "AND":
            val = "1"
            for i in self.interms:
                if i.value == "0":
                    val = "0"
                if val != "0":
                    if i.value == "U":
                        val = "U"
            self.value = val
            return val
        elif self.gatetype == "OR":
            val = "0"
            for i in self.interms:
                if i.value == '1':
                    val = "1"
                if val != "1":
                    if i.value == "U":
                        val = "U"
            self.value = val
            return val
        elif self.gatetype == "NAND":
            val = "0"
            for i in self.interms:
                if i.value == "0":
                    val = "1"
                if val != "1":
                    if i.value == "U":
                        val = "U"
            self.value = val
            return val
        elif self.gatetype == "NOT":
            if self.interms[0].value == "0":
                val = "1"
            elif self.interms[0].value == "1":
                val = "0"
            elif self.interms[0].value == "U":
                val = "U"
            else:
                print(self.interms[0].value)
                print(type(self.interms[0].value))
            self.value = val
            return val
        elif self.gatetype == "XOR":
            val = "0"
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    self.value = val
                    return val
            if val != "U":
                num_of_1 = 0
                for i in self.interms:
                    if i.value == "1":
                        num_of_1 = num_of_1 + 1
                val = num_of_1 % 2
                val = str(val)
                self.value = val
                return val
        elif self.gatetype == "XNOR":
            val = "0"
            for i in self.interms:
                if i.value == "U":
                    val = "U"
                    self.value = val
                    return val
            if val != "U":
                num_of_1 = 0
                for i in self.interms:
                    if i.value == "1":
                        num_of_1 = num_of_1 + 1
                val = num_of_1 % 2
                self.value = str(1 - val)
                return val
        elif self.gatetype == "NOR":
            val = "1"
            for i in self.interms:
                if i.value == "1":
                    val = "0"
                if val != "0":
                    if i.value == "U":
                        val = "U"
            self.value = val
            return val
        elif self.gatetype == "BUFF":
            val = self.interms[0].value
            self.value = val
            return val
        elif self.gatetype == "Input_to_gates":
            val = self.interms[0].value
            self.value = val
            return val

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

    node_innames = [i for i in tp_list]
    # now node_innames = [b', 256, c]

    return node_name, node_gatetype, node_innames


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
            node_list.append(n)

        elif line.startswith("OUTPUT"):
            index = line.find(")")
            name = line[7:index]
            o_name_list.append(name)

        else: # majority of internal gates processed here
            node_name, node_gatetype, node_innames = parse_gate(line)
            n = Node(node_name, "U", node_gatetype, node_innames)
            node_list.append(n)
            for b in node_innames:
                name = node_name + '-' + b
                a = Node(name, "U", "Input_to_gates", [b])
                node_list.append(a)
                n.interms.append(a)

    # now mark all the gates that are output as is_output
    for n in node_list:
        if n.name in o_name_list:
            n.is_output = True

    # link the interm nodes from parsing the list of node names (string)
    # example: a = AND (b, c, d)
    # thus a.innames = [b, c, d]
    # node = a, want to search the entire node_list for b, c, d
    for node in node_list:
        if node.gatetype == "Input_to_gates":
            for cur_name in node.innames:
                for target_node in node_list:
                    if target_node.name == cur_name:
                        node.interms.append(target_node)
    return


class circuit(object):
    def __init__(self, node_list, is_fault):
        self.node_list = node_list  # char: '0', '1', 'U' for unknown
        self.is_fault = is_fault
        self.faults = []
        self.input_list = []
        self.input_val = []
        self.output_list = []
        self.output_val = []
        # boolean: true if this wire is a fault of the circuit

    def simulation(self):
        updated_count = 1  # initialize to 1 to enter while loop at least once
        iteration = 0
        while updated_count > 0:
            updated_count = 0
            iteration += 1
            flag = 0
            output = 0
            for n in node_list:
                if self.is_fault:
                    for i in self.faults:
                        self.f_node = i[0]
                        self.f_val = i[1]
                        if n.name == self.f_node:
                            n.is_fault = True
                            n.value = self.f_val
                if n.value == "U":
                    n.calculate_value()
                    if n.is_output:
                        output += 1
                        if n.value == "0" or n.value == "1":
                            flag += 1
                        else:
                            flag += 0
                    if n.value == "0" or n.value == "1":
                        updated_count += 1
            if flag == output:
                break

    def display(self):  # print out the node nicely on one line
        self.input_list = [i.name for i in self.node_list if i.is_input]
        self.input_val = [i.value for i in self.node_list if i.is_input]

        self.output_list = [i.name for i in self.node_list if i.is_output]
        self.output_val = [i.value for i in self.node_list if i.is_output]
        return

def construct_fault_list(Node_list,n):
    fault_list = []
    fault_node = random.sample(Node_list,n)
    for n in fault_node:
        fault_list.append([n.name, '0',])
        fault_list.append([n.name, '1',])
    return fault_list

def cir_sim(faults, line_of_val):
    for node in node_list:
        node.set_value("U")

    strindex = 0
    for node in node_list:
        if node.is_input:
            if strindex > len(line_of_val) - 1:
                break
            node.set_value(line_of_val[strindex])
            strindex = strindex + 1

    circuit1 = circuit(node_list, False)
    circuit1.simulation()
    circuit1.display()

    for node in node_list:
        node.set_value("U")

    strindex = 0
    for node in node_list:
        if node.is_input:
            if strindex > len(line_of_val) - 1:
                break
            node.set_value(line_of_val[strindex])
            strindex = strindex + 1
    
    circuit2 = circuit(node_list, True)
    circuit2.faults = faults
    circuit2.simulation()
    circuit2.display()

    x = len(circuit1.output_val)
    
    if circuit1.output_val == circuit2.output_val:
        fault_detected = False
    else:
        l = len(circuit1.output_val)
        fault_detected = True
    return fault_detected

def n_counter(seed, n):
    #seed=seed[:bit]
    a = seed[2:]
    d = bin(int(a,16))[2:].zfill(4*len(a))
    d=d[:bit]
    s = '0b' + d
    tv_list = []
    if 2 ** n > 100:
        b = 100
    else:
        b = 2 ** n
    for i in range(b):
        c = int(s, 2) + 1
        s = '0b' + bin(c)[2:].zfill(len(d))
        if len(s[2:])>len(d):
         tv_list.append(s[3:])#removing any carry from the result
        else:
          tv_list.append(s[2:])

    return tv_list

def lfsr(h, seed):
    c = seed
    tv_list = []
    if bit > 8:
    #The following piece of code till the end of while loop is to concatenate the given hexadecimal seed and make it larger just in case it is not sufficient for a large bench 
     moreseed = len(seed)-4
     while bit > moreseed:
       c+=c
       moreseed = len(c)
       suffseed = moreseed % 8
       moreseed -= suffseed

    while True:
        d = ''
        for j in range(len(seed)//8):
            b = c[(j*8):(j*8)+8]
            a = b[-1]
            for i in range(1, len(h)):
                # print(a)
                if h[i] == '1':
                    a += str(int(b[i - 1], 2) ^ int(b[-1], 2))
                else:
                    a += str(int(b[i - 1], 2))
                    # print(a)
            b = a
            d += b
        c = d
        
        tv_list.append(c[:bit])
        if b == seed:
            break
        elif len(tv_list) >= 100:
            break
    return tv_list

# Returns factorial of n 
def fact(n): 
    res = 1 
    for i in range(2, n+1): 
        res = res * i     
    return res 

def nCr(n, r): 
    return (int(fact(n) / (fact(r) * fact(n - r)))) 
  
# Main function starts
print("\t\t***************************************************")
print('\t\t\t\t\t\t ECE-464 Project 3')
print("\t\t\tAre LFSRs good for covering multiple faults?")
print('\t\t***************************************************\n')
print("The following experiment setup is aimed at answering the following questions:\n\n1. If a given bench has multiple faults at a time, does LFSR still hold the reputation for generating random TVs that provide better fault coverage than other PRPGs?\n\n2. If so, does the LFSRs performance depend on the number of multiple faults tested?\n\nTo help us answer these questions, the following Fault simulator has been designed to simulate multiple faults of different combinations.\nA combination of length 2 would mean for example, a fault [a-0,b-1].Please not that each combination is treated as one fault for the circuit bench.\nFor the sake of the project, we have also set a limit on the total number of faults to be tested as 3000\n")

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
node_list = []
construct_nodelist()

if len(node_list)>20:
    sample_len = 3
elif len(node_list)<=20:
    sample_len = 1
n_fault = int(len(node_list)/sample_len)

#print(len(node_list))
#print(n_fault)
#print(type(n_fault))
fault_list = construct_fault_list(node_list, n_fault) #sample the no. of nodes
#print(fault_list)
#print(len(fault_list))
#print(comb(len(fault_list),4))

print ("-------------------------------------------------------------------\n")
comb_len=int(input("What combination length of faults do you want to test?(Please enter a decimal number)\n"))

final_faultcount = nCr(len(fault_list),comb_len)
if final_faultcount <= 3000:
  fault_comb = random.sample(list(it.combinations(fault_list,comb_len)),final_faultcount) # no. of faults.
else:
  fault_comb = random.sample(list(it.combinations(fault_list,comb_len)),3000)

multi_fault_list = []
for i in fault_comb:
    multi_fault_list.append(['0',i])
print("-------Full fault list -------")
print(f'\nTotal no. of faults {len(multi_fault_list)}.\n')

print ("-------------------------------------------------------------------\n")
tp_prpg = input("Which PRPG do you want to use?\n1. Enter '1' for n-bit counter\n2. Enter '2' for 8-bit LFSR\n3. Enter '3' to see the input list of TVs generated\n")

while True:
    if tp_prpg == '1' or tp_prpg == '2' or tp_prpg == '3':
        break
    else:
        tp_prpg = input("Please enter either 1, 2 or 3 in decimal format: ")

bit = 0
for nod in node_list:
    if nod.is_input:
        bit += 1

if tp_prpg == '1':
    seed = input("Please input the seed: ")
    while True:
        if len(seed) < bit//4:
            seed = input(f'Please enter seed with at least {bit} bits: ')
        else:
            break
    tv_list = n_counter(seed, bit)

if tp_prpg == '2':
    h_sel = input("\nPlease select the taps for lfsr:\nType '1' in integer for lfsr with no taps h = 10000000\nType '2' for lfsr with taps at 2,4,5 h = 10101100\nType '3' for taps at 2,3,4  h = 10111000\nType '4' for taps at 3,5,7 h = 10010101\nType '5' to give your own tap configuration\nYour Choice: ")
    while True:
        if h_sel == '1' or h_sel == '2' or h_sel == '3' or h_sel == '4' or h_sel == '5':
            break
        else:
            h_sel = input("Please input an integer from 1-5: ")
    if h_sel == '1':
        h = '10000000'
    elif h_sel == '2':
        h = '10101100'
    elif h_sel == '3':
        h = '10111000'
    elif h_sel == '4':
        h = '10010101'
    elif h_sel == '5':
        h = input("\nPlease enter the 8 bit h for your lfsr.\nIf the input is less than 8 bits the MSB bits will be taken as zero.\nIf it is greater than 8 only the first 8 bits will be considered.\nThe first bit is taken as 1 even if not entered as 1;")
        h = h.zfill(8)[-8:]
    seed = input("Please enter a seed in hex: ")
    while True:
        if len(seed)*4 >= 8:
            break
        else:
            seed = input("Please input an 8 bit seed: ")
    a = seed[2:]
    b = bin(int(a,16))[2:].zfill(4*len(a))
    tv_list = lfsr(h, b)

if tp_prpg == '3':
    tv_list = []
    isfile = input("Enter 1 to enter a file name or 2 to enter manually: ")
    while True:
        if isfile == '1':
            filename = input("Enter filename: ")
            f = open(filename, "r")
            for x in f:
                tv_list.append(x.replace("\n", ""))
            break
        elif isfile == '2':
            tv_list = list(map(str, input("Enter test vectors separated by spaces: ").split()))
            break
        else:
            print("Enter 1 or 2.")

print ("-------------------------------------------------------------------\n")


#loop_count = 0

#while loop_count < 10:
circuit_list = []
circuit_all = []
plot_list = []
#fdet_list = []
#count = 0
count_per = 1
for line_of_val in tv_list:
    fdet_list = []
    if len(line_of_val) < bit:
        line_of_val = (int((bit / len(line_of_val))) + 1) * line_of_val

    print(f'Using the input: {line_of_val}')
    if len(line_of_val) == 0:
        break

    for node in node_list:
        node.set_value("U")

    strindex = 0
    # Set value of input node
    for node in node_list:
        if node.is_input:
            if strindex > len(line_of_val) - 1:
                break
            node.set_value(line_of_val[strindex])
            strindex = strindex + 1

    #for node in node_list:
        #if node.is_input:
            #node.display()

    #fdet_list = []
    #fdet_list_all = []
    #print("")
    #print("--- Begin Simulation: ---")
    for i in range(len(multi_fault_list)):
        faults = multi_fault_list[i][1]
        if multi_fault_list[i][0] == '0':
            f_d = cir_sim(faults, line_of_val)
            if f_d:
                multi_fault_list[i][0]='1'
                a = ''
                for j in faults:
                    a += j[0] + '-' + j[1] + ' '
                fdet_list.append(a)
                #print(f'fault detected - {a}')

    if len(fdet_list) == 0:
        print("\nNone of the remaining faults were detected.")
    else:
        print(str(len(fdet_list)) + " faults detected with input " + line_of_val)
        # for x in range(len(fdet_list)):
        #     if x % 10 == 0 and x > 0:
        #         print("\n", end="")
        #     print(fdet_list[x], end="")
        #     if x < len(fdet_list) - 1:
        #         print(", ", end="")
        # print("")

    # create the csv string
    temp = ""
    for term in fdet_list:
        temp = temp + "," + term
    line = line_of_val + temp
    circuit_list.append(line)

    count = 0
    #undetected_faults = ''

    for n in multi_fault_list:
        #print(n)
        if n[0] == '0':
            count += 1

    # percentage data points generation
    if count_per % 10 == 0:
        per1 = len(multi_fault_list) - count    #len(circuit_list)
        per2 = len(multi_fault_list)
        per_plot = (per1/per2)*100
        plot_list.append(per_plot)
    print(plot_list)
    count_per += 1
    print(count_per)
    print(f'\nThere are {count} faults remaining. ')
    print("\n********************************************************************")
    print("")

if len(fault_list) > 0:
    print("Undetectable faults:")
    for n in multi_fault_list:
        if n[0] == '0':
            f = ''
            for m in n[1]:
                f += m[0] + '-' +m[1] + ' '
            #print(f'{f}')

# get the last test vector
temp = ""
for term in fdet_list:
    temp = temp + "," + term
line = line_of_val + temp
circuit_list.append(line)

with open('circuit_list.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    file.write("-------------------------------------------------" + "\n")
    for i in range(len(circuit_list) - 1):
        file.write(circuit_list[i] + "\n")

filename = wantToInputCircuitFile + ".csv"
print_list = []
if tp_prpg == "1":
    print_list.append("counter")
elif tp_prpg == "3":
    print_list.append("PRPG")
elif tp_prpg == "2":
    if h_sel == "1":
        print_list.append("LFSR1")
    if h_sel == "2":
        print_list.append("LFSR2")
    if h_sel == "3":
        print_list.append("LFSR3")
    if h_sel == "4":
        print_list.append("LFSR4")

#comb_list = ','.join(plot_list)
comb_list = []
comb_list = ','.join(str(e) for e in plot_list)
print_list.append(comb_list)

with open(filename, 'a') as csvfile:  
    # creating a csv writer object  
    csvwriter = csv.writer(csvfile)   
    #csvwriter.writerow(PRPG)    
    # writing the fields  
    csvwriter.writerow(print_list)

#plot_list = []
    

    #loop_count += 1
