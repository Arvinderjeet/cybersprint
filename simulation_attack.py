import os
import time

TARGET_DIR = "protected_folder"


def simulate_ransomware() :
	print( "😈 STARTING RANSOMWARE SIMULATION..." )
	
	# 1. Create dummy files
	for i in range( 10 ) :
		with open( f"{TARGET_DIR}/file_{i}.txt", "w" ) as f :
			f.write( "Important data" )
	
	time.sleep( 1 )
	print( "Files created. Starting encryption (renaming)..." )
	
	# 2. "Encrypt" them rapidly
	for i in range( 10 ) :
		try :
			os.rename( f"{TARGET_DIR}/file_{i}.txt", f"{TARGET_DIR}/file_{i}.locked" )
			print( f"Encrypted file_{i}" )
		except :
			pass
	# No sleep here = FAST changes = TRIGGER ALARM


if __name__ == "__main__" :
	if not os.path.exists( TARGET_DIR ) :
		os.makedirs( TARGET_DIR )
	simulate_ransomware()