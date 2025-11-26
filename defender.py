import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import deque


WATCH_DIR = "protected_folder"
THRESHOLD = 5
TIME_WINDOW = 1.0
CURRENT_THREAT_LEVEL = "SAFE"
LAST_DETECTED_EVENT = "None"


class RansomAwareHandler( FileSystemEventHandler ) :
	def __init__( self ) :
		self.changes = deque()
	
	def on_modified( self, event ) :
		self.check_behavior( event )
	
	def on_created( self, event ) :
		self.check_behavior( event )
	
	def on_moved( self, event ) :
		self.check_behavior( event )
	
	def check_behavior( self, event ) :
		global CURRENT_THREAT_LEVEL, LAST_DETECTED_EVENT
		
		current_time = time.time()
		self.changes.append( current_time )
		
		while self.changes and self.changes[ 0 ] < current_time - TIME_WINDOW :
			self.changes.popleft()
		
		if len( self.changes ) >= THRESHOLD :
			CURRENT_THREAT_LEVEL = "CRITICAL"
			LAST_DETECTED_EVENT = f"Rapid modification detected on: {os.path.basename( event.src_path )}"
			print( f"[!!!] ALERT: {LAST_DETECTED_EVENT}" )


def start_monitoring() :
	if not os.path.exists( WATCH_DIR ) :
		os.makedirs( WATCH_DIR )
		print( f"Created monitor directory: {WATCH_DIR}" )
	
	event_handler = RansomAwareHandler()
	observer = Observer()
	observer.schedule( event_handler, path = WATCH_DIR, recursive = False )
	observer.start()
	print( f"🛡️ Sentinel Active: Monitoring '{WATCH_DIR}'..." )
	
	try :
		while True :
			time.sleep( 1 )
	except KeyboardInterrupt :
		observer.stop()
	observer.join()