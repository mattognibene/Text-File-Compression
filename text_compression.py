import math
import pickle


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


# String -> Dict
# returns a dict where the key is the character and the value is how many time it occurs
def create_occurences(content):
    occ = {}
    for i in range(len(content)):
        for letter in content[i]:
            if letter in occ:
                occ[letter] = occ[letter] + 1
            else:
                occ[letter] = 1
    return occ

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
        sorted[largest] = d[largest]
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



#bytearray Tree -> String
def decompress():
    file_name = input("Enter the file name (NOTE! do not include the -out.bin or -enc.p. \n"
                      "If the file is doc-out.bin and doc-enc.p, simply enter \"doc\"")
    t = pickle.load(open(file_name+"-enc.p","rb"))
    bin = open(file_name+"-out.bin","rb")
    print(ba)
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

def pad_zeros(b):
    while len(b) < 8:
        b = b + "0"
    return b

def pad_zeros_before(b):
    while len(b) < 8:
        b = "0" + b
    return b

#Bitstring -> Bytearray
#takes a bit string and divides them into a bytearray. The final byte is always the position
#of the final meaningful bit of the byte before it
def divide_to_bytes(final):
    bytes = []
    q = 0
    while q < len(final):
        if q + 8 > len(final):
            bytes.append(pad_zeros(final[q:]))
            bytes.append(pad_zeros_before(bin(len(final[q:]) - 1)[2:]))
            q = len(final)
        else:
            bytes.append(final[q:q + 8])
            q = q + 8
    '''data = []
    for i in bytes:
        data.append(bytearray(int(i, 2)))
    return data'''
    ints = []
    for i in bytes:
        ints.append(int(i, 2))
    data = []
    for i in ints:
        data.append(bytearray([i]))
    return data


#String Encodement -> Bitstring
#returns the final text encoded
def encode_text(content, encodement):
    final = ""
    for i in range(len(content)):
        for letter in content[i]:
            final += encodement[letter]
    return final

#Bytearray Huffman String-> .bin .p
#creates two files, one of the encoded text, one one the encodement
def output(bytarry,hf,name):
    new_file = open(remove_tag(name) + "-out.bin", 'wb')
    for i in bytarry:
        new_file.write(i)
    pickle.dump(hf, open(remove_tag(name)+"-enc.p", "wb"))

#main fuction for compressing
def compress():
    file_name = input("Enter file name")
    file = open(file_name, "r")
    content = file.readlines()
    file.close()
    occ = create_occurences(content)

    #huffman->the tree representation of th encodement
    huffman = create_tree(list(sort_dict(find_probabilities(occ)).items()))
    #encodement->a dict where the letter is the key and its encodement the value
    encodement = encode_tree(huffman, "")
    encoded_text = encode_text(content,encodement)
    print(encoded_text)
    #output(divide_to_bytes(encoded_text),huffman,file_name)
    new_file = open('out.bin', 'wb')
    for i in divide_to_bytes(encoded_text):
        new_file.write(i)

    pickle.dump(huffman, open("enc.p", "wb"))
    print(len(divide_to_bytes(encoded_text)))

    print("compression succesful!")
    #todo statistics on how much space was saved
    print("Compression saved as " + remove_tag(file_name)+"-enc.p and " + remove_tag(file_name)+"-out.bin")
    print("note: both files are necessary for decompression")


#String->String
#removes tags such as .txt and .bin from file names
def remove_tag(str):
    return str[0:str.index(".")]
def main():
    choice = input("Press [1] to compress. \n"
                   "Press [2] to decompress")
    while(not(choice=="1" or choice=="2")):
        choice = input("Press [1] to compress. \n"
                       "Press [2] to decompress")
    if choice == "1":
        compress()
    else:
        decompress()

main()