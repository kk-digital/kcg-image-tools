from IntegerEncoder import IntegerEncoder


def example_1(): 
    '''Example for binary encoding.
    '''
    encoder = IntegerEncoder()

    print(encoder.encode(5 , 4 , 'binary'))
    
def example_2(): 
    '''Example for grey encoding.
    '''
    encoder = IntegerEncoder()

    print(encoder.encode(26 , 8 , 'grey'))
