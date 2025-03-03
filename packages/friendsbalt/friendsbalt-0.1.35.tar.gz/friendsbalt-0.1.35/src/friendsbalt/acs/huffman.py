from .pq import MinPQ

class HuffmanEncoding:
    """
    A class to perform Huffman Encoding and Decoding.

    This class can either encode a given source text or decode a given encoded text using a provided Huffman tree.

    Attributes:
        src (str): The source text to be encoded.
        encoded_text (str): The encoded text to be decoded.
        tree (Node): The root node of the Huffman tree.
        dictionary (dict): A dictionary mapping characters to their Huffman codes.

    Methods:
        encoding():
            Returns the encoded text as a string of 0s and 1s.
        source_text():
            Returns the original source text.
        root():
            Returns the root node of the Huffman tree.
    """
    def __init__(self, src=None, encoded_text=None, root=None):
        """
        Initializes a new Huffman Encoding. Either source text or encoded text and root must be provided.
        If source text is provided, it builds the Huffman tree and dictionary, and encodes the text.
        If encoded text and root are provided, it decodes the text.
        Args:
            src (str, optional): The source text to be encoded.
            encoded_text (str, optional): The encoded text to be decoded.
            root (Node, optional): The root node of the Huffman tree for decoding.
        """
        if src is not None:
            self.src = src
            self.tree = self._build_tree()
            self.dictionary = self._build_dictionary()
            self.encoded_text = self._encode()
        
        if encoded_text is not None and root is not None:
            self.encoded_text = encoded_text
            self.tree = root
            self.src = self._decode()
    
    class Node:
        def __init__(self, freq, char=None, left=None, right=None):
            self.char = char
            self.freq = freq
            self.left = left
            self.right = right
        
        def is_leaf(self):
            return self.char is not None
    
    def _build_tree(self):
        if self.src is None: raise ValueError("Encoding source cannot be None.")
        freqs = {}
        for char in self.src:
            freqs[char] = freqs.get(char, 0) + 1

        pq = MinPQ()
        for char, freq in freqs.items():
            pq.insert(freq, self.Node(freq, char))

        while pq.size() > 1:
            left = pq.del_min()
            right = pq.del_min()
            merged = self.Node(left.freq + right.freq, left=left, right=right)
            pq.insert(merged.freq, merged)
        
        return pq.del_min()
    
    def _encode(self):
        return ''.join(self.dictionary[char] for char in self.src)
    
    def _decode(self):
        decoded_text = []
        node = self.tree
        for bit in self.encoded_text:
            node = node.left if bit == '0' else node.right
            if node.char is not None:
                decoded_text.append(node.char)
                node = self.tree
        return ''.join(decoded_text)

    def encoding(self):
        """
        Returns the encoded text.
        Returns:
            str: The encoded text as a string of 0s and 1s.
        """
        return self.encoded_text

    def source_text(self):
        """
        Returns the original source text.
        Returns:
            str: The original source text.
        """
        return self.src

    def root(self):
        """
        Returns the root node of the Huffman tree.
        Returns:
            Node: The root node of the Huffman tree.
        """
        return self.tree
    
    def _build_dictionary(self, node=None, prefix=''):
        """
        Recursively builds a dictionary that maps characters to their corresponding
        Huffman codes based on the Huffman tree.
        Args:
            node (Node, optional): The current node in the Huffman tree. Defaults to None,
                                   which means the function will start from the root node.
            prefix (str, optional): The current Huffman code prefix. Defaults to an empty string.
        Returns:
            dict: A dictionary where keys are characters and values are their corresponding
                  Huffman codes.
        """
        if node is None:
            node = self.tree
        
        if node.char is not None:
            return {node.char: prefix}
        
        dictionary = {}
        dictionary.update(self._build_dictionary(node.left, prefix + '0'))
        dictionary.update(self._build_dictionary(node.right, prefix + '1'))
        return dictionary
    
class HuffmanFile:
    """
    A class for reading and writing Huffman encoded files.

    This class provides a bridge between the Huffman Encoding abstraction and the bits written to a binary file.

    Attributes:
        file_path (str): The path to the file to read from or write to.
        encoding (HuffmanEncoding): The HuffmanEncoding instance to be written to or read from the file.

    Methods:
        write():
            Write Huffman tree and encoded data to binary file.
        read():
            Read Huffman tree and encoded data from binary file.
    """
    def __init__(self, file_path, raw_string=None):
        self.file_path = file_path
        if raw_string is not None:
            self.encoding = HuffmanEncoding(src=raw_string)
        else:
            self.encoding = None

    def __enter__(self):
        self.file = open(self.file_path, 'wb' if self.encoding else 'rb')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
    
    def _serialize_tree(self, node):
        """Serialize Huffman tree to string of bits"""
        if node.is_leaf():
            # Leaf node: 0 + 8-bit character
            return '0' + format(ord(node.char), '08b')
        # Internal node: 1 + left + right
        return '1' + self._serialize_tree(node.left) + self._serialize_tree(node.right)
    
    def write(self):
        """Write Huffman tree and encoded data to binary file"""
        if not self.encoding:
            raise ValueError("Encoding must be provided for writing")
        
        # Serialize tree
        tree_bits = self._serialize_tree(self.encoding.root())
        
        # Write tree size and tree
        self.file.write(len(tree_bits).to_bytes(4, byteorder='big'))
        tree_int = int(tree_bits, 2)
        tree_bytes = (len(tree_bits) + 7) // 8
        self.file.write(tree_int.to_bytes(tree_bytes, byteorder='big'))
        
        # Write encoded data
        encoded_text = self.encoding.encoding()
        self.file.write(len(encoded_text).to_bytes(4, byteorder='big'))
        data_int = int(encoded_text, 2)
        data_bytes = (len(encoded_text) + 7) // 8
        self.file.write(data_int.to_bytes(data_bytes, byteorder='big'))
    
    def _deserialize_tree(self, bits, pos=0):
        """Reconstruct Huffman tree from bits"""
        if bits[pos] == '0':
            char = chr(int(bits[pos+1:pos+9], 2))
            return HuffmanEncoding.Node(1, char=char), pos + 9
        left, new_pos = self._deserialize_tree(bits, pos=pos + 1)
        right, final_pos = self._deserialize_tree(bits, pos=new_pos)
        return HuffmanEncoding.Node(1, left=left, right=right), final_pos
    
    def read(self):
        """Read Huffman tree and encoded data from binary file"""
        if self.encoding:
            raise ValueError("Encoding should not be provided for reading")
        
        # Read and reconstruct tree
        tree_size = int.from_bytes(self.file.read(4), byteorder='big')
        tree_bytes = (tree_size + 7) // 8
        tree_int = int.from_bytes(self.file.read(tree_bytes), byteorder='big')
        tree_bits = bin(tree_int)[2:].zfill(tree_size)
        root, _ = self._deserialize_tree(tree_bits)
        
        # Read encoded data
        data_size = int.from_bytes(self.file.read(4), byteorder='big')
        data_bytes = (data_size + 7) // 8
        data_int = int.from_bytes(self.file.read(data_bytes), byteorder='big')
        encoded_text = bin(data_int)[2:].zfill(data_size)
        
        self.encoding = HuffmanEncoding(encoded_text=encoded_text, root=root)
        return self.encoding.source_text()