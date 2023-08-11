from collections import Counter
from ordered_list import *
from huffman_bit_writer import *
from huffman_bit_reader import *
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char   # stored as an integer - the ASCII character code value
        self.freq = freq   # the frequency associated with the node
        self.left = None   # Huffman tree (node) to the left
        self.right = None  # Huffman tree (node) to the right
        
    def __eq__(self, other):
        '''Needed in order to be inserted into OrderedList'''
        return type(other) == HuffmanNode and self.freq == other.freq and self.char == other.char
        
    def __lt__(self, other):
        '''Needed in order to be inserted into OrderedList'''
        if self.freq == other.freq:
            return self.char < other.char
        return self.freq < other.freq

class FileNotFoundError(Exception):
    pass

letters = "abcdefghijklmnopqrstuvwxyz"
def cnt_freq(filename):
    '''Opens a text file with a given file name (passed as a string) and counts the 
    frequency of occurrences of all the characters within that file'''
    frequency = [0]*256
    try:
        with open(filename) as file:
            counter = Counter(file.read())
            for key, value in counter.items():
                frequency[ord(key)] = value
        return frequency
    except IOError:
        raise FileNotFoundError(filename + " not found")

def create_huff_tree(char_freq):
    '''Create a Huffman tree for characters with non-zero frequency
    Returns the root node of the Huffman tree'''
    ol = OrderedList()
    for i in range(len(char_freq)):
        if char_freq[i] != 0:
            ol.add(HuffmanNode(i, char_freq[i]))
    parent = None
    while not ol.is_empty():
        pop1 = ol.pop(0)
        try:
            pop2 = ol.pop(0)
        except:
            parent = pop1
            break
        if pop1 < pop2:
            parent = HuffmanNode(min(pop1.char, pop2.char), pop1.freq + pop2.freq)
            parent.left = pop1
            parent.right = pop2
        ol.add(parent)
    return parent

def create_code(node):
    '''Returns an array (Python list) of Huffman codes. For each character, use the integer ASCII representation 
    as the index into the array, with the resulting Huffman code for that character stored at that location'''
    huff = [""]*256
    create_code_helper(node, "", huff)
    return huff

def create_code_helper(treenode, string, huffman):
    if treenode is not None:
        if treenode.left is None and treenode.right is None:
            huffman[treenode.char] = string # treenode.char is ASCII value for character, assign path code to correct index
        else:
            create_code_helper(treenode.left, string + "0", huffman)
            create_code_helper(treenode.right, string + "1", huffman)


def create_header(freqs):
    '''Input is the list of frequencies. Creates and returns a header for the output file
    Example: For the frequency list asscoaied with "aaabbbbcc, would return "97 3 98 4 99 2" '''
    string = ""
    for i in range(len(freqs)):
        if freqs[i] != 0:
            string += str(i) + " " + str(freqs[i]) + " "
    string = string[0:len(string)-1]
    return string


def huffman_encode(in_file, out_file):
    '''Takes inout file name and output file name as parameters - both files will have .txt extensions
    Uses the Huffman coding process on the text from the input file and writes encoded text to output file
    Also creates a second output file which adds _compressed before the .txt extension to the name of the file.
    This second file is actually compressed by writing individual 0 and 1 bits to the file using the utility methods 
    provided in the huffman_bits_io module to write both the header and bits.
    Take not of special cases - empty file and file with only one unique character'''
    frequencies = cnt_freq(in_file)
    tree = create_huff_tree(frequencies)
    codes = create_code(tree)
    compressed = ""
    for i in range(len(out_file)):
        if out_file[i] == ".":
            compressed += "_compressed"
        compressed += out_file[i]
    huffman = ""
    with open(in_file) as infile:
        for line in infile:
            for character in line:
                huffman += codes[ord(character)]

    bitwriter = HuffmanBitWriter(compressed)
    output_file = open(out_file, "w")
    header = create_header(cnt_freq(in_file))
    output_file.write(header + "\n")
    bitwriter.write_str(header + "\n")
    output_file.write(huffman)
    bitwriter.write_code(huffman)
    output_file.close()
    bitwriter.close()



def huffman_decode(encoded_file, decode_file): # Project 3B
    try:
        hbr = HuffmanBitReader(encoded_file)
    except:
        raise FileNotFoundError
    hbw = HuffmanBitWriter(decode_file)
    frequencies = parse_header(hbr.read_str())
    tree = create_huff_tree(frequencies)
    treenode = tree
    decode = ""
    total = sum(frequencies)
    while len(decode) < total: # Iterate while there are characters to be added
        if treenode is not None and treenode.left is None and treenode.right is None:
            # If it is a leaf then add the character to the decode string
            # Start from the beginning
            decode += chr(treenode.char)
            treenode = tree
        else:
            readbit = hbr.read_bit()
            if readbit: # If a 1 is read, go right
                treenode = treenode.right
            else: # If a 0 is read, go left
                treenode = treenode.left
    # Write the decoded string to the file
    decode_file = open(decode_file, "w")
    decode_file.write(decode)
    hbw.write_str(decode)
    decode_file.close()
    hbw.close()
    hbr.close()

def parse_header(header_string):
    header_string = header_string[:len(header_string) - 1]
    if header_string == "":
        return [0]*256
    header_array = header_string.split()
    indices = [int(header_array[i]) for i in range(len(header_array)) if i % 2 == 0]
    frequencies_file = [int(header_array[i]) for i in range(len(header_array)) if i % 2 != 0]
    frequencies = [0] * 256
    for i in range(len(indices)):
        frequencies[indices[i]] = frequencies_file[i]
    return frequencies

if __name__ == '__main__':
    frequencies = [0]*256
    frequencies[ord("a")] = 16
    frequencies[ord("b")] = 7
    frequencies[ord("c")] = 51
    frequencies[ord("d")] = 19
    frequencies[ord("e")] = 8
    print(create_code(create_huff_tree(frequencies))[ord("e")])