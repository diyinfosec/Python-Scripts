#!/usr/bin/python

'''
 * Author: Ramprasad Ramshankar 
 * Alias: diyinfosec
 * Date: 17-01-2020
 * Purpose: Base64 Encode/Decode, without using the Python base64 module. 
 * Language:  Python
'''

"""
Conceptual Reference:
https://code.tutsplus.com/tutorials/base64-encoding-and-decoding-using-python--cms-25588
https://stackoverflow.com/questions/4080988/why-does-base64-encoding-require-padding-if-the-input-length-is-not-divisible-by
"""


"""
 Base64 encoding uses the following charset: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
 crypt() encoding uses this charset: ./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
 """
b64_map='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
b64_size=6;
b64_pad_char='=';



"""
Base64 encoding steps:
1. Convert all characters in the input string to their ascii equivalent number (i.e. a:97, b:98, etc)
2. Convert all the above numbers into their binary equivalents: 8-bit and zero prefixed (i.e. 97: 01100001).
3. Concatenate all these binary numbers into a single "bit" string. 
4. Divide this bit string into smaller slices each containing 6 bits (i.e. 011000 and so on)
5. If the last slice contains less than 6 bits then suffix it with by the number of deficient zeroes.
6. Take each slice and map it to it's Base64 equivalent. The output string will be the set of all these mappings. 
7. Optional: If padding is required, calculate 'How many more characters should I add to make the input string a multiple of 3?' Let's say this is X. 
8. Suffix the output string with X number of padding characters. (Default will be 0 or no padding characters.)

Base64 decoding steps:
1. Remove padding characters (if present) from the end of the input string. 
2. Get the index of each character in the input string in the Base64 map. 
3. Convert each character into it's binary equivalent: 8-bit and zero prefixed. 
4. Knock-off the first two bits from each binary string, concatenate the result into a single string (?)
5. Divide this string into smaller slices each containing 8 bits. 
6. Convert 8-bit numbers to their decimal equivalents.
7. Convert the decimal to character. 

"""
def base64_encode(s,padding_reqd):
#{
	
	#- Calculate padding bytes (if padding is required)
	pad_bytes=0;
	if(padding_reqd=='Y'):
		pad_bytes=len(s)%3;
		if pad_bytes >0:
			pad_bytes=3-pad_bytes;


	#- Convert the string into binary representation
	"""
	https://stackoverflow.com/questions/18815820/convert-string-to-binary-in-python
	https://stackoverflow.com/questions/16926130/convert-to-binary-and-keep-leading-zeros-in-python
	https://www.journaldev.com/23689/python-string-append
	"""

	s2bin=''.join(format(ord(x),'08b') for x in s);
	#print s2bin;


	#- Cut the binary string into slices of 6 characters each and append to a list. 
	s2bin_len=len(s2bin);
	num_parts=s2bin_len/b64_size;

	str_start=0;
	str_end=b64_size;
	bin_list=[];

	for x in range(num_parts):
		#print s2bin[str_start:str_end];
		#print s2bin[str_end:]
		bin_list.append(s2bin[str_start:str_end])
		str_start+=b64_size;
		str_end+=b64_size;

	#- Suffix the last part with trailing zeroes to make the length equal to 6.
	zeros_to_add=s2bin_len%b64_size;
	#print 'Zeroes to add is', zeros_to_add;
	if zeros_to_add!=0:
		bin_list.append(s2bin[str_end-b64_size:]+'0'*(b64_size-zeros_to_add));


	#- Map to base64
	out_str=''
	for x in bin_list:
		#print x;
		#print int(x,2);
		out_str+=''.join(b64_map[int(x,2)]);

	#- Account for padding characters
	out_str+=b64_pad_char*pad_bytes;
	
	#- Return output string
	return out_str;
#}



"""
Base64 decoding steps:
1. Remove padding characters (if present) from the end of the input string. 
2. Get the index of each character in the input string in the Base64 map. 
3. Convert each character into it's binary equivalent: 6-bit and zero prefixed and put it into a single string. 
4. Divide this string into smaller slices each containing 8 bits. 
5. Convert 8-bit numbers to their decimal equivalents.
6. Convert the decimal to character. 
"""
def base64_decode(s):
#{
	
	#- Strip the padding characters and get index of the rest of the chars into the list (steps 1 and 2)
	#- https://www.pythonforbeginners.com/basics/list-comprehensions-in-python
	l=[b64_map.find(x) for x in s.strip(b64_pad_char)];
	#print l;

	#- Concatenated bit string (step 3)
	l2binstr=''.join(format(x,'06b') for x in l);
	#print l2binstr;


	#- Cut the binary string into slices of 8 characters each and append to a list (step 4)
	l2binstr_len=len(l2binstr);
	
	#- Will this always be a multiple of 8?
	num_parts=l2binstr_len/8;

	str_start=0;
	str_end=8;
	bin_list=[];

	for x in range(num_parts):
		bin_list.append(l2binstr[str_start:str_end])
		str_start+=8;
		str_end+=8;

	
	#- Convert decimals back to characters (step 6)
	out_str=''
	for x in bin_list:
		out_str=out_str+''.join(chr(int(x,2)));
		
	return out_str

#}



# TESTING

#- Get the input string to encode
#inp_str=raw_input('Enter string to encode: ')

padding_reqd='Y';
print base64_encode('helloworld',padding_reqd);

print base64_decode('cmFtcHJhc2Fk');
print base64_decode('aQ==');
print base64_decode('ZHNhZg==');
print base64_decode('dGhpcyBpcyBob3cgYWxsIHRoc2UgdGhpbmdzIGhhcHBlbiBpbiBsaWZlLCBob3BlIHRoZXJlIGlzIGEgd2F5LiB3aGVyZSB0aGVyZSBpcyBhIHdpbGwgdGhlcmUgaXMgYSB3YXksIGlzIHRoaXMgbW9yZSB0aGFuIDI0IGNoYXJhY3RlcnMhISE=');
