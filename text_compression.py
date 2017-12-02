import math
import pickle
#file_name = input("Enter file name")

file = open("smp.txt", "r")
content = file.readlines()
file.close()
#todo make these functions like a good programmer
dict = {}
for i in range(len(content)):
    for letter in content[i]:
        if letter in dict:
            dict[letter] = dict[letter]+1
        else:
            dict[letter] = 1

#A Branch is one of the following
# - String
# - split_node
# - negative 1

#A split_node is a split_node(Branch Branch)
class split_node(object):
    def __init__(self, left, right):
        self.left=left
        self.right=right
    def __copy__(self):
        return split_node(self.left,self.right)



#list of Pair -> Branch
#returns the huffman tree representation of the given dict
#the list must be sorted
def create_tree(pairs):
    if len(pairs)==0:
        return -1
    to_be_added = []
    next = pairs[0][1]
    #todo helper?
    for x in pairs:
        if (x[1] == next):
            to_be_added.append(x)

    pairs=pairs[len(to_be_added):]

    return split_node(create_branch_from_list(to_be_added),
               create_tree(pairs))


# [List-of Pairs] -> Branch
# creates a branch from a given list of numbers where each leaf is on the same layer
def create_branch_from_list(tba):
    if (len(tba) == 1):
        return tba[0][0]
    else:
        return split_node(
            create_branch_from_list(first_half(tba)),
            create_branch_from_list(second_half(tba))
        )

    # List -> List
    # todo purpose
def first_half(l):
    return l[:math.floor(len(l) / 2)]

def second_half(l):
    return l[math.floor(len(l) / 2):]








#Dict -> Dict
#returns a dict where each component is value of the component in d divided by the sum
def find_probabilities(d):
    probabilities = {}
    for component in d:
        probabilities[component] = d[component]/sum_dict(d)
    return probabilities

#Dict -> Int
#sums all the numbers associated in the given dict
def sum_dict(d):
    sum = 0
    for component in d:
        sum+=d[component]
    return sum

#Dict -> New Dict
#sorts a dict with the largest first
#todo, use something better than a linear sort
def sort_dict(d):
    temp = {}
    for comp in d:
        temp[comp] = d[comp]
    sorted = {}
    for i in (range(len(temp))):
        largest = next(iter(temp))
        for it in temp:
            if temp[it] > temp[largest]:
                largest = it
        sorted[largest] = dict[largest]
        del temp[largest]
    return sorted

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

#Branch String-> Dict
#returns a dict where the key is the letter and the value is its encoding
#Accumulator: keeps track of which directions we have already been to
def encode_tree(b,acc):
    if isinstance(b,str):
        return{b:acc}
    elif b==-1:
        return {}
    else:
        return merge_two_dicts(encode_tree(b.left, acc+"0"),
                               encode_tree(b.right, acc+"1"))

huffman = create_tree(list(sort_dict(find_probabilities(dict)).items()))
encodement = encode_tree(huffman, "")
final = ""
for i in range(len(content)):
    for letter in content[i]:
        final+=encodement[letter]

def pad_zeros(b):
    while len(b) < 8:
        b = b + "0"
    return b
def pad_zeros_before(b):
    while len(b) < 8:
        b =  "0"  + b
    return b


#todo make al this shit into function
bytes = []
q=0
#please fix this hack
while q<len(final):
    if q+8>len(final):
        bytes.append(pad_zeros(final[q:]))
        bytes.append(pad_zeros_before(bin(len(final[q:])-1)[2:]))
        q=len(final)
    else:
        bytes.append(final[q:q+8])
        q=q+8

ints = []
for i in bytes:
    ints.append(int(i, 2))
data = []
for i in ints:
    data.append(bytearray([i]))
new_file = open('out.bin', 'wb')

for i in data:
    new_file.write(i)

pickle.dump(huffman, open("hf.p", "wb"))

#bytearray Tree -> String
def decompress(ba,t):
    bs = cleave_extra(bytearray_to_string(ba))
    text = ""
    path=t.__copy__()
    for i in bs:
        if i=="0":
            path = path.left
        else:
            path=path.right
        if type(path)==str:
            text+=path
            path = t.__copy__()
    return text


#list of bytearray->String
def bytearray_to_string(ba):
    build=""
    for i in ba:
        build+=(pad_zeros_before(str(bin(i[0]))[2:]))
    return build

#bitstring -> bitstring
def cleave_extra (bs):
    final_bit = int(bs[-8:],2)
    return bs[:(len(bs)- (8-final_bit) +1)-8]
