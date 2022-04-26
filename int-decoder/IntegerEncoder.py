from io import UnsupportedOperation
import numpy as np 
import unittest

class IntegerEncoder: 
    """Encoder of integer values into a set of other encoding formats. (Binary and grey-decoded) are only supported now. 
    """
    def __init__(self) -> None:
        return 
    
    
    def __binary_encoder(self, value: int, number_of_bits: int = 32) -> list: 
        """ a function to encode a given integer into its binary representation or 2's complement if a -ve integer was given. 
        :param value: The integer value to be encoded. 
        :type value: int
        :param number_of_bits: the width of the binary representation 
        :type number_of_bits: int
        :returns: list of integers as the binary representation of the given value
        :rtype: list[int]
        """
        return [int(bit) for bit in np.binary_repr(value , number_of_bits)]
    
    def __grey_encoder(self, value: int , number_of_bits: int = 32) -> list: 
        """ a function to encode a given integer into its grey encoded representation. 
        :param value: The integer value to be encoded. 
        :type value: int
        :param number_of_bits: the width of the representation 
        :type number_of_bits: int
        :returns: list of integers as the grey encoded representation of the given value
        :rtype: list[int]
        """

        #gets the binary representation and reverse it to start with the Least bit
        binary_repr = self.__binary_encoder(value , number_of_bits)
        binary_repr.reverse()
        
        grey_encoded = [] 
        
        for i in range(len(binary_repr) - 1):
            #the grey encoder formula is (gn = 1 - bn if bn == 1 else gn = bn)
            if binary_repr[i + 1] == 1:
                grey_encoded.append(1 - binary_repr[i])
            else:
                grey_encoded.append(binary_repr[i])
        
        #Leave the last bit as it's 
        grey_encoded.append(binary_repr.pop())
        
        grey_encoded.reverse()
    
        return grey_encoded
    
    def encode(self, value: int,  number_of_bits: int = 32, type: str = "binary") -> list: 
        """ a function to encode a given integer into the slected encodings type 
        :param value: The integer value to be encoded. 
        :type value: int
        :param number_of_bits: the width of the representation 
        :type number_of_bits: int
        :returns: list of integers as the encoded representation of the given value
        :rtype: list[int]
        """

        if type == "binary": 
            return self.__binary_encoder(value , number_of_bits)
        
        elif type == "grey": 
            return self.__grey_encoder(value , number_of_bits)
        else: 
            raise UnsupportedOperation("This type of encoding is not supported.")
        
        
class IntegerEncoderTest(unittest.TestCase): 
    
    def test_binary_encoding(self):
        encoder = IntegerEncoder()
        
        self.assertEqual(encoder.encode(0 , 4 , 'binary') , [0 , 0 , 0 , 0]) 
        self.assertEqual(encoder.encode(15 , 8 , 'binary') , [0 , 0 , 0 , 0 , 1 , 1 , 1 , 1]) 
        self.assertEqual(encoder.encode(128 , 4 , 'binary') , [1 , 0 , 0 , 0 , 0 , 0 , 0 , 0]) 
        self.assertEqual(encoder.encode(0 , 64 , 'binary') , [0] * 64) 
                     
    def test_grey_encoding(self):
        encoder = IntegerEncoder()
        
        self.assertEqual(encoder.encode(0 , 4 , 'grey') , [0 , 0 , 0 , 0]) 
        self.assertEqual(encoder.encode(59 , 8 , 'grey') , [0 , 0 , 1 , 0 , 0 , 1 , 1 , 0]) 
        self.assertEqual(encoder.encode(15 , 8 , 'grey') , [0 , 0 , 0 , 0 , 1 , 0 , 0 , 0]) 
        self.assertEqual(encoder.encode(0 , 64 , 'grey') , [0] * 64) 
                     
if __name__ == '__main__':
    unittest.main()
