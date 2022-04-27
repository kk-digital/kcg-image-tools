# IntegerEncoder
> A standalone tool for encoding integers into other chosen codes. 

## Description

The tool takes in a single integer value and encodes it into a different form from the available implemented encodings methods.

## Supported Encodings

Here is a list of the supported codes which you can convert the integer value into on of them. 
- Binary Encodings. 
- Grey code Encodings. 

## Installation
All that's needed to start using IntegerEncoder is to install the dependencies using the command.
```
pip install -r src/to/dir/requirements.txt
```

## Method Documentations

Using the IntegerEncoder is too simple and straightforward, you can simply call the method called `encode` providing the integer value,length of the output list, encoding type below you can see description of each of them. 

* `value` _[int]_ - _[required]_ - The integer value to be encoded. 
* `number_of_bits` _[int]_ - _[optional]_ - The desired length of the output list, default is `32`. 

* `type` _[str]_ - _[optional]_ - The type of encoding to be applied to `value`, default is `binary` supported types are: 
    * `binary` for binary encodings 
    * `grey` for grey coded representation of `value` 


The methods returns a list representing the resulted encodings, first value of the list is the most significant bit and so on. 

## Example Usage

Example1: Encoding an integer into its `binary` representation. 
```python 
from IntegerEncoder import IntegerEncoder

encoder = IntegerEncoder()

print(encoder.encode(5 , 4 , 'binary'))
```

The result in the std output is
```
[0, 1, 0, 1]
```
Example2: Encoding an integer into its `grey` code representation. 
```python 
from IntegerEncoder import IntegerEncoder

encoder = IntegerEncoder()

print(encoder.encode(26 , 8 , 'grey'))
```

The result in the std output is
```
[0, 0, 0, 1, 0, 1, 1, 1]
```