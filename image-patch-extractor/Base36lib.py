

class Base36: 
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def encode(s) -> str: 
        
        number = 0 
        
        #convert the given object to int depending on the provided type. 
        if isinstance(s, int): 
            number = s 
        elif isinstance(s, str): 
            number = int.from_bytes(bytes(s , 'ascii'), 'big')
        elif isinstance(s, bytes): 
            number = int.from_bytes(s, 'big')
        else: 
            raise TypeError("Provided type can be integer, string or bytes only.")
        
        is_negative = (number < 0) 
        
        number = abs(number)

        alphabet, base36 = ['0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', '']

        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36
        if is_negative:
            base36 = '-' + base36

        return base36 or alphabet[0]


    @staticmethod
    def decode(base36) -> int: 
        return int(base36, 36)