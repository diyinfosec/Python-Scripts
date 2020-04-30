from timeit import default_timer as timer
from hashlib import sha1
import json

'''
import win32api

drives = win32api.GetLogicalDriveStrings()
drives = drives.split('\000')[:-1]
print(drives)

'''
SECTOR_SIZE = 512
MFT_RECORD_SIZE = 1024

def read_boot_record(fd):
			#- Reading the BIOS parameter block and locating the $MFT
			#- TODO - Instead of hardcoding SECTOR_SIZE see if you can read say 1000 bytes and determine the sector size form there. 
			#- TODO - Derive size of the MFT record from the BPB
		first_sector = fd.read(SECTOR_SIZE)

		'''
		11 - Bytes per sector - 2 bytes
		13 - Sectors per cluster - 1 byte
		48 - MFT Cluster Number - 8 bytes
		Ref: https://www.delftstack.com/howto/python/how-to-convert-bytes-to-integers/
		'''
		bytes_per_sector = int.from_bytes(first_sector[11:13:],byteorder='little')
		sectors_per_cluster = int.from_bytes(first_sector[13:14:],byteorder='little')
		cluster_size = bytes_per_sector * sectors_per_cluster
		mft_cluster_num = int.from_bytes(first_sector[48:56:],byteorder='little')		
		
		mft_offset = (mft_cluster_num * cluster_size) 

		print('Bytes per sector is %s'%(bytes_per_sector))
		print('Sectors per cluster is %s'%(sectors_per_cluster))
		print('MFT cluster number is %s'%(mft_cluster_num))
		print('Offset to MFT is %s'%(mft_offset))

		d={}

		d['cluster_size'] = cluster_size
		d['mft_offset'] = mft_offset

		return d

def read_mft_record(fd,offset):
		#- Reading the FILE record of $MFT
		#- Seek should ALWAYS be a multiple of sector size for direct disk access. 
		#- Refer: https://support.microsoft.com/en-ie/help/100027/info-direct-drive-access-under-win32
		fd.seek(offset)
		
		return fd.read(MFT_RECORD_SIZE)

def parse_data_runs(data_run_bytes, cluster_size):
	bytes_to_skip=0
	counter=1
	data_run_list=[]
	dr_temp=[]
	prev_cluster_offset=0
	for x in data_run_bytes:
		if bytes_to_skip==0:
			#- Added to handle last data run (which is always 00)
			#- Ref: https://flatcap.org/linux-ntfs/ntfs/concepts/data_runs.html
			if int(x)==0:
				break

			val1=int(hex(x)[3])
			val2=int(hex(x)[2])
			#print(val1)	
			#- Take val1 bytes, this will be the num_clusters
			num_clusters = int.from_bytes(data_run_bytes[counter:counter+val1], byteorder='little')
			#print(num_clusters)
			
			#- Take val2 bytes, this will be the cluster_offset
			#- Interpreting Cluster Offset as a 'Signed' integer as per: https://www.sciencedirect.com/topics/computer-science/starting-cluster
			cluster_offset = int.from_bytes(data_run_bytes[counter+val1:counter+val1+val2], byteorder='little', signed=True) + prev_cluster_offset
			#print(cluster_offset)

			prev_cluster_offset = cluster_offset

			data_run_list.append([cluster_offset*cluster_size, num_clusters*cluster_size])
			dr_temp.append([num_clusters, cluster_offset])

			bytes_to_skip=val1 + val2
		else:
			bytes_to_skip=bytes_to_skip-1
		counter=counter+1
		#print(hex(x))

	print(dr_temp)

	#print(data_run_list)
	return data_run_list	
	#print(len(data_run_list))


#- This is a bad non-generic function, intended to process only $MFT
def process_record_zero(mft_record_ideal):

		#- TODO: Generic processing function for MFT record.
		#- Apply fixup if the $DATA attribute exceeds 1 cluster. 
		'''
		24 - Real Size of MFT record for $MFT - 4 bytes
		260 - Size of MFT data attribute - 4 bytes
		0x48 - MFT Cluster Number - 8 bytes
		'''
		mft_record_data_attr_size = int.from_bytes(mft_record_ideal[260:264:],byteorder='little')
		#print('Size of $MFT data attribute  is %s'%(mft_record_data_attr_size))


		mft_data_attribute = mft_record_ideal[256:256+mft_record_data_attr_size:]
		#print('$MFT data attribute contents %s'%(mft_data_attribute))

		mft_data_run_offset = int.from_bytes(mft_data_attribute[32:40], byteorder='little')
		print('MFT data run begins at offset %s'%(mft_data_run_offset))

		mft_data_run=bytearray(mft_data_attribute[mft_data_run_offset:])
		#print('MFT data run is %s'%(mft_data_run))

		return mft_data_run	

#- Todo, just pass the drive letter and add the slashes later.
def take_mft_snapshot(source_drive,target_path,filename_counter):
	#- Open the file
	with open(source_drive,'rb') as f:

		#- Get all the metadata you need to dump the $MFT file.
		boot_data=read_boot_record(f)
		cluster_size=boot_data['cluster_size']
		mft_record_ideal = read_mft_record(f, boot_data['mft_offset']) 
		mft_data_run=process_record_zero(mft_record_ideal)
		mft_data_run_list=parse_data_runs(mft_data_run, cluster_size) 
		
		#- TODO - Accept filename as argument.
		#- TODO - This can be generic like icat 
		snapshot_filename=target_path+ "MFT"+str(filename_counter) + ".bin"
		print(snapshot_filename)


		snapshot_file = open(snapshot_filename, "wb")
		hash_list=[]
		
		#- Walking through the Data Runs and 
		for x in mft_data_run_list:
			start_offset=x[0]
			total_bytes=x[1]
			f.seek(start_offset)

			#- Read only cluster_size bytes at a time
			#- Calculate hash of those bytes and append to a list
			required_reads=int(total_bytes/cluster_size)
			#print('Required reads ', required_reads)
			disk_str=bytearray(b'')
			for y in range(required_reads):
					mft_bytes=f.read(cluster_size)
					hash_list.append(sha1(mft_bytes).hexdigest())
					# write to file
					snapshot_file.write(mft_bytes)
			
		snapshot_file.close()

		#- TODO: This can return snapshot name, timestamp, hash filename as a dictionary

		#print(hash_list)
		print('Clusters in this snapshot: ',len(hash_list))
		hash_filename=snapshot_filename+"_hashes.txt"
		hash_file=open(hash_filename,"w")
		hash_file.write(json.dumps(hash_list))
		
		#- TODO: Comparing lists use: 
		# https://stackoverflow.com/questions/57531712/compare-corresponding-elements-of-a-list
		#- Closing the disk file
		f.close()


'''
TODO: Maybe config parser to get inputs?	
TODO
source_drive	and target_path as inputs
Warning if source/target drive letters are not same
Check if you are running as administrator
List the NTFS drives
'''	

try:
	start_time=timer()

	source_drive=r"\\.\g:"
	target_path=r"D:\\"

	filename_counter=0

	while True:
			print("This program will take a snapshot of the $MFT in %s and write the output file to %s"%(source_drive,target_path))
			print("You an keep taking snapshots and press ctrl+c to quit the program")
			input('Press enter to take a snapshot. Ctrl+c to Quit. ');
			take_mft_snapshot(source_drive,target_path,filename_counter)
			filename_counter=filename_counter+1
except KeyboardInterrupt:
	print("\nCancelled by user. Snapshots taken: ", filename_counter)




end_time = timer()
print("Time taken %2f"%(end_time-start_time))
