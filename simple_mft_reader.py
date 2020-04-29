from timeit import default_timer as timer

'''
import win32api

drives = win32api.GetLogicalDriveStrings()
drives = drives.split('\000')[:-1]
print(drives)

Public Type BOOT_RECORD
Jump(2) As Byte
OEMID(7) As Byte
BPB As BIOS_PARAMETERS_BLOCK
EBPB As EXTENDED_BIOS_PARAMETERS_BLOCK
BootStrap(425) As Byte
BootSignature As Integer
Padding As Long
Padding As Long
End Type
'''

filename=r"\\.\c:"
SECTOR_SIZE = 512
MFT_RECORD_SIZE = 1024

try:
	#- Open the file
	with open(filename,'rb') as f:

		#- Reading the BIOS parameter block and locating the $MFT
		first_sector = f.read(SECTOR_SIZE)

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
		

		#- Reading the FILE record of $MFT
		#- Seek should ALWAYS be a multiple of sector size for direct disk access. 
		#- Refer: https://support.microsoft.com/en-ie/help/100027/info-direct-drive-access-under-win32
		f.seek(mft_offset)
		mft_record_ideal = f.read(MFT_RECORD_SIZE)

		'''
		24 - Real Size of MFT record for $MFT - 4 bytes
		260 - Size of MFT data attribute - 4 bytes
		0x48 - MFT Cluster Number - 8 bytes
		'''
		mft_record_data_attr_size = int.from_bytes(mft_record_ideal[:4:],byteorder='little')
		print('Size of $MFT data attribute  is %s'%(mft_record_data_attr_size))


		mft_data_attribute = mft_record_ideal[256:256+mft_record_data_attr_size:]
		#print('$MFT data attribute contents %s'%(mft_data_attribute))

		mft_data_run_offset = int.from_bytes(mft_data_attribute[32:40], byteorder='little')
		print('MFT data run begins at offset %s'%(mft_data_run_offset))

		mft_data_run=bytearray(mft_data_attribute[mft_data_run_offset:])
		#print('MFT data run is %s'%(mft_data_run))

		bytes_to_skip=0
		counter=1
		data_run_list=[]
		dr_temp=[]
		prev_cluster_offset=0
		for x in mft_data_run:
			if bytes_to_skip==0:
				#- Added to handle last data run (which is always 00)
				#- Ref: https://flatcap.org/linux-ntfs/ntfs/concepts/data_runs.html
				if int(x)==0:
					break

				val1=int(hex(x)[3])
				val2=int(hex(x)[2])
				#print(val1)	
				#- Take val1 bytes, this will be the num_clusters
				num_clusters = int.from_bytes(mft_data_run[counter:counter+val1], byteorder='little')
				#print(num_clusters)
				
				#- Take val2 bytes, this will be the cluster_offset
				#- Interpreting Cluster Offset as a 'Signed' integer as per: https://www.sciencedirect.com/topics/computer-science/starting-cluster
				cluster_offset = int.from_bytes(mft_data_run[counter+val1:counter+val1+val2], byteorder='little', signed=True) + prev_cluster_offset
				#print(cluster_offset)

				prev_cluster_offset = cluster_offset

				data_run_list.append([cluster_offset*cluster_size, num_clusters*cluster_size])
				#dr_temp.append([num_clusters, cluster_offset])

				bytes_to_skip=val1 + val2
			else:
				bytes_to_skip=bytes_to_skip-1
			counter=counter+1
			#print(hex(x))

		print(data_run_list)
		#print(len(data_run_list))

		#print(dr_temp)

		newFile = open("MFT.bin", "wb")
		
		#- Walking through the Data Runs and 
		for x in data_run_list:
			required_offset=x[0]
			required_bytes=x[1]
			f.seek(required_offset)
			mft_bytes=f.read(required_bytes)
			
			# write to file
			newFile.write(mft_bytes)
		
		newFile.close()

		#- Closing the disk file
		f.close()
		
except KeyboardInterrupt:
	print("User cancelled before end of file")



end_time = timer()
