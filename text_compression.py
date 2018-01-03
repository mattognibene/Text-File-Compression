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

#A pair is a pair(Any Number)
class pair(object):
    def __init__(self, val, num):
        self.val = val
        self.num = num

#Compression
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

# Dict -> List of Pairs
def create_pairs(occ):
    lop = []
    for omega in occ:
        lop.append(pair(omega,occ[omega]))
    return lop

#LoP -> Lop
#sorts a list of pair
def sort_list_of_pair(lop):
    #todo please stop being lazy and make this merge sort
    temp = []
    for i in lop:
        temp.append(i)
    sorted = []
    for i in (range(len(temp))):
        smallest = temp[0]
        index=0
        for it in temp:
            if it.num < smallest.num:
                smallest = it
                index=temp.index(smallest)

        sorted.append(smallest)
        del temp[index]
    return sorted

# List of Pairs -> Tree
#takes a dict of the occurences and creates a huffman tree
def create_tree(lop):
    while len(lop)>1:
        lop = combine_lowest(lop)

    return lop[0].val

#List of Pair -> Lst of Pair
#takes a list of pair but with the two lowest pairs combined into a tree
def combine_lowest(lop):
    sorted =sort_list_of_pair(lop)
    tree=split_node(sorted[1].val,sorted[0].val)
    sorted.append(pair(tree,(sorted[0].num+sorted[1].num)))
    del sorted[0]
    del sorted[0]
    return sorted

#Branch String-> Dict
#returns a dict where the key is the letter and the value is its encoding
#Accumulator: keeps track of which directions we have already been to
def encode_tree(b,acc):
    if isinstance(b,str):
        return{b:acc}
    elif b==None:
        return {}
    else:
        return merge_two_dicts(encode_tree(b.left, acc+"0"),
                               encode_tree(b.right, acc+"1"))

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

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
    ints = []
    for i in bytes:
        ints.append(int(i, 2))
    data = []
    for i in ints:
        data.append(bytearray([i]))
    return data

#main fuction for compressing
def compress():
    file_name = input("Enter file name")
    file = open(file_name, "r")
    content = file.readlines()
    file.close()
    occ = create_occurences(content)

    #huffman->the tree representation of th encodement
    huffman = create_tree(create_pairs(occ))
    #encodement->a dict where the letter is the key and its encodement the value
    encodement = encode_tree(huffman, "")
    encoded_text = encode_text(content,encodement)
    #output(divide_to_bytes(encoded_text),huffman,file_name)
    new_file = open(remove_tag(file_name)+'-out.bin', 'wb')
    for i in divide_to_bytes(encoded_text):
        new_file.write(i)

    pickle.dump(huffman, open(remove_tag(file_name)+"-enc.p", "wb"))

    print("compression succesful!")
    #todo statistics on how much space was saved
    print("Compression saved as " + remove_tag(file_name)+"-enc.p and " + remove_tag(file_name)+"-out.bin")
    print("note: both files are necessary for decompression")

#Decompression
#binary -> String
#converts a binary number into a string rep of it as a byte
def bin_to_bytestring(b):
    return pad_zeros_before(b[2:])

#bitstring -> bitstring
def cleave_extra (bs):
    final_bit = int(bs[-8:],2)
    return bs[:(len(bs)- (8-final_bit) +1)-8]

#bitstring tree -> string
def read_encodemenet(bs, t):
    text=""
    path = t.__copy__()
    for i in bs:
        if i == "0":
            path = path.left
        else:
            path = path.right
        if type(path) == str:
            text += path
            path = t.__copy__()
    return text

#list of bytearray->String
def bytearray_to_string(ba):
    build=""
    for i in ba:
        build+=(pad_zeros_before(str(bin(i[0]))[2:]))
    return build


def pad_zeros(b):
    while len(b) < 8:
        b = b + "0"
    return b

def pad_zeros_before(b):
    while len(b) < 8:
        b = "0" + b
    return b


#bytearray Tree -> String
def decompress():
    file_name = input("Enter the file name (NOTE! do not include the -out.bin or -enc.p. \n"
                      "If the file is doc-out.bin and doc-enc.p, simply enter \"doc\"")
    t = pickle.load(open(file_name+"-enc.p","rb"))
    bin_f = open(file_name+"-out.bin","rb")
    ba = bin_f.read()
    bs = ""
    for i in ba:
        bs+= bin_to_bytestring(bin(i))

    bs = cleave_extra(bs)
    text = read_encodemenet(bs,t)

    print("Decompressed file saved as "+ file_name +".txt")
    new_file = open(file_name+".txt","w+")
    new_file.write(text)


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