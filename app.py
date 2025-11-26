import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import psutil
import pandas as pd
import datetime
import webbrowser
import os
import threading
import time
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = dash.Dash( __name__, external_stylesheets = [ dbc.themes.CYBORG ] )
app.title = "Ransom-Halt | Sentinel"

WATCH_DIR = "protected_folder"
if not os.path.exists( WATCH_DIR ) :
	os.makedirs( WATCH_DIR )

VIRUS_DIR = "quarantine_zone"
# if not os.path.exists( VIRUS_DIR ) :
# 	os.makedirs( VIRUS_DIR )

SYSTEM_STATE = {
	"status" : "SECURE",
	"last_event" : "System Normal",
	"cpu_history" : deque( maxlen = 60 ),
	"defender_threat" : "SAFE"  # Logic from the original defender script
	}

# Initialize CPU history
for _ in range( 60 ) : SYSTEM_STATE[ "cpu_history" ].append( 0 )

class RansomAwareHandler( FileSystemEventHandler ) :
	def __init__( self ) :
		self.changes = deque()
		self.THRESHOLD = 5
		self.TIME_WINDOW = 1.0
	
	def process_event( self, event ) :
		current_time = time.time()
		self.changes.append( current_time )
		while self.changes and self.changes[ 0 ] < current_time - self.TIME_WINDOW :
			self.changes.popleft()
		
		if len( self.changes ) >= self.THRESHOLD :
			SYSTEM_STATE[ "defender_threat" ] = "CRITICAL"
			SYSTEM_STATE[ "last_event" ] = f"RANSOMWARE: Rapid changes in {os.path.basename( event.src_path )}"
	
	def on_modified( self, event ) :
		self.process_event( event )
	
	def on_moved( self, event ) :
		self.process_event( event )
	
	def on_created( self, event ) :
		self.process_event( event )


def start_sentinel() :
	event_handler = RansomAwareHandler()
	observer = Observer()
	observer.schedule( event_handler, path = WATCH_DIR, recursive = False )
	observer.start()
	try :
		while True : time.sleep( 1 )
	except :
		observer.stop()

monitor_thread = threading.Thread( target = start_sentinel, daemon = True )
monitor_thread.start()

def scan_virus_folder() :
	KNOWN_VIRUSES = [ "trojan.exe", "wannacry.bat", "malware.py", "keylogger.dll", "ransomware.lock", "virus.scr"]
	try :
		files = os.listdir( VIRUS_DIR )
		for file in files :
			if file in KNOWN_VIRUSES :
				return True, file
	except FileNotFoundError :
		pass
	return False, None


def drop_virus_file() :
	with open( f"{VIRUS_DIR}/trojan.exe", "w" ) as f :
		f.write( "DUMMY MALICIOUS CODE" )


def clean_virus_folder() :
	try :
		if os.path.exists( f"{VIRUS_DIR}/trojan.exe" ) :
			os.remove( f"{VIRUS_DIR}/trojan.exe" )
	except :
		pass


def get_process_list() :
	processes = [ ]
	for proc in psutil.process_iter( [ 'pid', 'name', 'cpu_percent', 'memory_percent' ] ) :
		try :
			pinfo = proc.info
			status = "Trusted"
			if pinfo[ 'cpu_percent' ] > 20 :
				status = "Suspicious (High Load)"
			if pinfo[ 'name' ] in [ 'python.exe', 'cmd.exe', 'powershell.exe' ] and pinfo[ 'cpu_percent' ] > 5 :
				status = "Potential Script"
			processes.append( pinfo )
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) :
			pass
	
	df = pd.DataFrame( processes )
	if not df.empty :
		df = df.sort_values( by = 'cpu_percent', ascending = False ).head( 10 )
		df[ 'Risk Level' ] = df[ 'cpu_percent' ].apply(
			lambda x : 'CRITICAL' if x > 50 else ('WARNING' if x > 20 else 'SAFE') )
	return df


def generate_report_file( df ) :
	timestamp = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
	html_content = f"""
    <html>
    <head><title>Ransom-Halt Incident Report</title></head>
    <body style="font-family: Arial; padding: 20px; background-color: #f0f0f0;">
        <h1 style="color: #d9534f;">Ransom-Halt Security Report</h1>
        <h3>Generated at: {timestamp}</h3>
        <hr>
        <h2>System Snapshot</h2>
        {df.to_html( classes = 'table table-striped' )}
        <div style="background-color: #dff0d8; padding: 10px; border: 1px solid #3c763d; color: #3c763d;">
            <strong>Status:</strong> Threat Neutralized.
        </div>
    </body>
    </html>
    """
	filename = "incident_report.html"
	with open( filename, "w" ) as f :
		f.write( html_content )
	return filename


app.layout = dbc.Container( [
	dbc.Row( [
		dbc.Col( html.H1( "🛡️ RANSOM-HALT", className = "text-center text-primary mb-4" ), width = 12 )
		], className = "mt-4" ),

	dbc.Row( [
		dbc.Col( dbc.Card( [
			dbc.CardHeader( "CPU Usage" ),
			dbc.CardBody( html.H2( id = "cpu-text", className = "text-center" ) )
			], color = "secondary", inverse = True ), width = 4 ),
		
		dbc.Col( dbc.Card( [
			dbc.CardHeader( "RAM Usage" ),
			dbc.CardBody( html.H2( id = "ram-text", className = "text-center" ) )
			], color = "secondary", inverse = True ), width = 4 ),
		
		dbc.Col( dbc.Card( [
			dbc.CardHeader( "Threat Status" ),
			dbc.CardBody( html.H2( id = "status-text", className = "text-center", style = {"color" : "#5cb85c"} ) )
			], color = "secondary", inverse = True ), width = 4 ),
		], className = "mb-4" ),
	
	dbc.Row( [
		# Live Graph
		dbc.Col( [
			dbc.Card( [
				dbc.CardHeader( "Real-Time System Load" ),
				dbc.CardBody( dcc.Graph( id = "live-graph", style = {"height" : "300px"} ) )
				], color = "dark", inverse = True )
			], width = 8 ),
		
		dbc.Col( [
			dbc.Card( [
				dbc.CardHeader( "⚠️ VIRUS LAB", className = "bg-warning text-dark fw-bold" ),
				dbc.CardBody( [
					html.P( "Test Signature Engine:" ),
					dbc.Button( "⬇️ Drop 'trojan.exe'", id = "btn-drop", color = "danger", className = "w-100 mb-2" ),
					dbc.Button( "🧹 Clean Zone", id = "btn-clean", color = "success", className = "w-100" ),
					html.Hr(),
					dcc.Graph( id = "risk-pie", style = {"height" : "150px"} )  # Moved Pie here
					] )
				], color = "dark", inverse = True )
			], width = 4 ),
		], className = "mb-4" ),
	
	# Bottom Section: Process Table & Controls
	dbc.Row( [
		dbc.Col( [
			html.H4( "Suspicious / High Load Processes", className = "text-white" ),
			html.Div( id = "process-table-container" ),
			], width = 12 )
		] ),
	
	# Footer Controls
	dbc.Row( [
		dbc.Col(
			dbc.Button( "📄 Generate Incident Report", id = "btn-report", color = "info", className = "mt-3",
			            n_clicks = 0 ),
			width = {"size" : 3, "offset" : 9}
			)
		] ),
	
	dcc.Interval( id = 'interval-component', interval = 1000, n_intervals = 0 ),
	
	# Hidden divs
	html.Div( id = "report-status" ),
	html.Div( id = "hidden-virus-status" )
	
	], fluid = True )


@app.callback(
	[ Output( "cpu-text", "children" ),
	  Output( "ram-text", "children" ),
	  Output( "status-text", "children" ),
	  Output( "status-text", "style" ),
	  Output( "live-graph", "figure" ),
	  Output( "risk-pie", "figure" ),
	  Output( "process-table-container", "children" ) ],
	[ Input( "interval-component", "n_intervals" ),
	  Input( "btn-drop", "n_clicks" ),
	  Input( "btn-clean", "n_clicks" ) ]
	)
def update_metrics( n, btn_drop, btn_clean ) :
	# button
	ctx = callback_context
	if ctx.triggered :
		trigger_id = ctx.triggered[ 0 ][ "prop_id" ].split( "." )[ 0 ]
		if trigger_id == "btn-drop" :
			drop_virus_file()
		elif trigger_id == "btn-clean" :
			clean_virus_folder()
			SYSTEM_STATE[ "defender_threat" ] = "SAFE"  # Reset
	
	is_virus, virus_name = scan_virus_folder()
	
	ransom_status = SYSTEM_STATE[ "defender_threat" ]
	
	status_msg = "SECURE"
	status_color = {"color" : "#5cb85c"}  # Green
	
	if is_virus :
		status_msg = f"⚠️ VIRUS DETECTED: {virus_name}"
		status_color = {"color" : "#d9534f", "animation" : "blinker 1s linear infinite"}
	elif ransom_status == "CRITICAL" :
		status_msg = "⚠️ RANSOMWARE ATTACK!"
		status_color = {"color" : "#d9534f", "animation" : "blinker 1s linear infinite"}
	
	cpu = psutil.cpu_percent( interval = 0.1 )
	ram = psutil.virtual_memory().percent
	df = get_process_list()
	
	if status_msg != "SECURE" :
		gauge_color = "red"
	elif cpu > 80 :
		gauge_color = "orange"
		if status_msg == "SECURE" : status_msg = "HIGH LOAD"
	else :
		gauge_color = "#00cc96"
	
	# Line Graph
	fig_line = go.Figure( go.Indicator(
		mode = "gauge+number", value = cpu,
		domain = {'x' : [ 0, 1 ], 'y' : [ 0, 1 ]},
		title = {'text' : "CPU Load"},
		gauge = {'axis' : {'range' : [ None, 100 ]}, 'bar' : {'color' : gauge_color}}
		) )
	fig_line.update_layout( paper_bgcolor = "rgba(0,0,0,0)", font = {'color' : "white"},
	                        margin = dict( t = 30, b = 0, l = 20, r = 20 ) )
	
	# Pie Chart
	if not df.empty :
		fig_pie = px.pie( df, names = 'Risk Level', hole = 0.4,
		                  color_discrete_map = {'SAFE' : 'green', 'WARNING' : 'orange', 'CRITICAL' : 'red'} )
		fig_pie.update_layout( paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)",
		                       font = {'color' : "white"}, margin = dict( t = 0, b = 0, l = 0, r = 0 ),
		                       showlegend = False )
	else :
		fig_pie = go.Figure()
	
	# Table
	if not df.empty :
		table = dbc.Table.from_dataframe( df[ [ 'pid', 'name', 'cpu_percent', 'Risk Level' ] ],
		                                  striped = True, bordered = True, hover = True)
	else :
		table = html.P( "No active processes found." )
	
	return f"{cpu}%", f"{ram}%", status_msg, status_color, fig_line, fig_pie, table


@app.callback(
	Output( "report-status", "children" ),
	[ Input( "btn-report", "n_clicks" ) ]
	)
def generate_report( n ) :
	if n > 0 :
		df = get_process_list()
		filename = generate_report_file( df )
		webbrowser.open( 'file://' + os.path.realpath( filename ) )
		return "Report Generated!"
	return ""


if __name__ == '__main__' :
	app.run( debug = True, use_reloader = False )