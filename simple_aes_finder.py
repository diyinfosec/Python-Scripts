from binascii import b2a_hex, unhexlify, hexlify
from math import log
from timeit import default_timer as timer

#- Important configuration 
aes_key_size=32
entropy_limit=4



key_file_name='aes_256_keys.txt'



# - Setting the file name
#f1=open(key_file_name,'w')
filename='3_EFS_Files_Created_only_Not_opened.vmem'
#filename='sample.bin'
filename="04-FEK_data_stucture.bin"


#- Variables related to file processing
file_offset=0;
total_keys_passing_entropy = 0;
total_keys_checked = 0;

start_time = timer()

try:
	#- Open the file
	with open(filename, 'rb') as f:



		#- Read till you find data
		while True:
			#- Seek to the new file offset
			f.seek(file_offset)

			#- Read the keysize number of bytes
			temp_key=f.read(aes_key_size)
			
			#- Exit condition 1: If the read buffer is less than 32 bytes:
			if len(temp_key) < aes_key_size:
				break
			
			#- Exit condition 2: When there are no more bytes to be read from the file:
			if not temp_key:
				break

			#- Increment total number of keys checked
			total_keys_checked = total_keys_checked +1;
			#- Entropy calculation
			d_byte_occurrences={}
			for b in temp_key:
				if(b in d_byte_occurrences):
					d_byte_occurrences[b]=d_byte_occurrences[b]+1
				else:
					d_byte_occurrences[b]=1

			entropy=0
			for value in d_byte_occurrences.values():
				p = value/aes_key_size;
				entropy = entropy + ((p*log(p))/log(2))

			print("Entropy is ", entropy)
			if(-entropy > entropy_limit):
				#print("Entropy is ", entropy)
				#print(b2a_hex(temp_key))
				total_keys_passing_entropy = total_keys_passing_entropy + 1


			#- Increment file offset one byte at a time
			file_offset=file_offset+1

			#print(d_byte_occurrences)
			
			#- Append the key to the key list
			#print(temp_key.encode('hex'))
			# key_list.append(temp_key.encode('hex'))
			#f1.write(temp_key.encode('hex')+'\n')
except KeyboardInterrupt:
	print("User cancelled before end of file")



end_time = timer()
print("Total keys evaluated: ", total_keys_checked)
print("Total keys having Entropy >%d: %d"%(entropy_limit, total_keys_passing_entropy))
print("Current offset:", file_offset)
print("Time elapsed = ", end_time-start_time)

	#f1.close()
