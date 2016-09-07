import json
import re #regular expression
import sqlite3
import datetime
import dateutil.parser

class DIRMONParser(object):
	
	def __init__(self):
		global sqllitedb
		global db
		global jsonFileEntry
		
		jsonFileEntry = { 'version':1, 'start_ts':'?', 'host_name':'?' }
		#print json.dumps(jsonFileEntry, indent=2)
		
		sqllitedb = sqlite3.connect(':memory:')
    
		db = sqllitedb.cursor()    
		db.execute('SELECT SQLITE_VERSION()')
		
		sqlite_version = db.fetchone()
		
		db.executescript('''
		CREATE TABLE DIRMON_FILELIST
		(
			loop_no  	integer
		,   loop_ts  	text
		,   host_name 	text
		,	file_name 	text
		,   file_ext  	text
		,   file_size 	integer
		,   file_ts  	text
		,   filename_ts text
		);
		
		CREATE TABLE DIRMON_LOOP_SUMMARY
		(
			loop_no              integer
		,	loop_ts              text
		,	host_name            text
		,	ob_file_count        integer
		,	ob_file_size         integer
		,	ob_file_oldest_ts    text
		,   ob_file_latest_ts    text
		,   ob_file_oldest_age   integer
		,   ob_file_latest_age   integer
		,   all_file_count       integer
		,	all_file_size        text
		);
		
		CREATE TABLE DIRMON_FILE_SUMMARY
		(
			file_name     text
		,   loop_no_first integer
		,   loop_no_last  integer
		,   first_seen_ts  text
		,   last_seen_ts   text
		,   age           integer
		);
		''')

		print "---------------------"
		print "Starting DIRMONParser"
		print "Using SQLite version: %s" % sqlite_version   
		print "---------------------"

	# ====================================================================
	# UTIL / SUPPORT FUNCTIONS
	# ====================================================================
	def is_numeric(self,numeric_string):
		#Returns True for all non-unicode numbers
		try:
			numeric_string = numeric_string.decode('utf-8')
		except:
			return False
			pass
		try:
			float(numeric_string)
			return True
		except:
			return False
			pass
	
	# ====================================================================
	# DB FUNCTIONS
	# ====================================================================
	def save_filelist_entry( self ):
		sql_stmt = ("""
			insert into DIRMON_FILELIST
			(
			  loop_no
			, loop_ts
			, host_name 	
			, file_name 	
			, file_ext  	
			, file_size 	
			, file_ts  	
			, filename_ts
			)
			values
			(
			  %s
			, '%s'
			, '%s'
			, '%s'
			, '%s'
			, %s
			, '%s'
			, '%s'
			)
		"""		
			%
		    ( 
			  jsonFileEntry['loop_no']
			, jsonFileEntry['loop_ts']
			, jsonFileEntry['host_name']
			, jsonFileEntry['file_name']
			, jsonFileEntry['file_ext']
			, jsonFileEntry['file_size']
			, jsonFileEntry['file_ts']
			, jsonFileEntry['file_name_ts']
			)
		)
		
		db.execute(sql_stmt)

	def process_file_summary(self):
		print "\nProcess File Summary..."
		sql_stmt = ("""
			insert into DIRMON_FILE_SUMMARY
			(
			  file_name   
			, loop_no_first
			, loop_no_last 
			, first_seen_ts 
			, last_seen_ts  
			, age
			)
			select file_name   
				 , min(loop_no) as loop_no_first
				 , max(loop_no) as loop_no_last 
				 , min(loop_ts) as first_seen_ts 
				 , max(loop_ts) as last_seen_ts  
				 , 0 as age	
			  from DIRMON_FILELIST
			 group by file_name
		"""		
		)
		db.execute(sql_stmt)
		
		for r in db.execute("SELECT COUNT(*) FROM DIRMON_FILE_SUMMARY"):
			print '--> Rows loaded into DIRMON_FILE_SUMMARY: %s' % r[0]

	def process_loop_summary(self):
		print "\nProcess Loop Summary..."

		sql_stmt = ("""
		  insert into DIRMON_LOOP_SUMMARY
		  (
			 loop_no
		   , loop_ts
		   , host_name
		   , ob_file_count
		   , ob_file_size
		   , ob_file_oldest_ts
		   , ob_file_latest_ts
		   , ob_file_oldest_age
		   , ob_file_latest_age
		   , all_file_count
		   , all_file_size
		  )
		  SELECT af.loop_no
		       , af.loop_ts
			   , af.host_name
			   , df.ob_file_count
			   , df.ob_file_size
			   , df.ob_file_oldest_ts
			   , df.ob_file_latest_ts
			   , 0 as ob_file_oldest_age
			   , 0 as ob_file_latest_age
			   , af.all_file_count
			   , af.all_file_size
			FROM (
				SELECT loop_no
					 , loop_ts
					 , host_name
					 , count(1)       as all_file_count
					 , sum(file_size) as all_file_size
				  FROM DIRMON_FILELIST
				 group by loop_no
				        , loop_ts
						, host_name
				) as af
				inner join
				(
				SELECT dfl.loop_no
					 , dfl.loop_ts
					 , count(1)                as ob_file_count
					 , sum(dfl.file_size)      as ob_file_size
					 , min(dfs.first_seen_ts)  as ob_file_oldest_ts
					 , max(dfs.first_seen_ts)  as ob_file_latest_ts
				  FROM DIRMON_FILELIST dfl
				       inner join DIRMON_FILE_SUMMARY dfs
					     on (dfl.file_name = dfs.file_name)
				 WHERE dfl.file_ext = 'dat'
				 group by dfl.loop_no
				        , dfl.loop_ts
				) as df
				on af.loop_no = df.loop_no
			""" )
			
		db.execute(sql_stmt)
		
		for r in db.execute("SELECT COUNT(*) FROM DIRMON_LOOP_SUMMARY"):
			print '--> Rows loaded into DIRMON_LOOP_SUMMARY: %s' % r[0]
		
		#DEBUG
		#for r in db.execute("SELECT * FROM DIRMON_LOOP_SUMMARY"):
		#	print r
			
	# ====================================================================
	# PARSE FUNCTIONS
	# ====================================================================
	def parse_header(self, line_parts):
		if line_parts[0] == "--START-LOOP":
			jsonFileEntry['loop_no'] = line_parts[1]
			return False
		elif line_parts[0] == "Start":
			jsonFileEntry['start_ts'] = line_parts[1]
		elif line_parts[0] == "Hostname":
			jsonFileEntry['host_name'] = line_parts[1]
		else:
			pass
		
		return True

	def parse_file_entry(self, line_parts):
		if line_parts[0] == "--START-LOOP":
			jsonFileEntry['loop_no'] = line_parts[1]
		elif line_parts[0] == "TS":
			ts = line_parts[1]
			ts_len = len(ts)
			if ts[10:11] == ":":
				jsonFileEntry['loop_ts'] = ts[0:10] + " " + ts[11:ts_len]
			else:
				jsonFileEntry['loop_ts'] = ts;
		elif len(line_parts) == 8:
			#a file entry
			jsonFileEntry['file_size'] = line_parts[4]
			jsonFileEntry['file_date'] = line_parts[5]
			jsonFileEntry['file_time'] = line_parts[6]
			jsonFileEntry['file_name'] = line_parts[7]
			
			jsonFileEntry['file_ts'] = datetime.datetime.strptime(line_parts[5] + " " + line_parts[6],"%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")
			
			file_ext_parts = re.split("\.",jsonFileEntry['file_name'])
			if len(file_ext_parts) > 1:
				arr_size = len(file_ext_parts)
				jsonFileEntry['file_ext'] = file_ext_parts[arr_size-1]
			else:
				jsonFileEntry['file_ext'] = "undef"
			
			file_name_formatted = jsonFileEntry['file_name'].replace(":"," ").replace("_"," ").replace("."," ").replace("-"," ")
			file_name_parts = re.split(" ",file_name_formatted)
			if len(file_name_parts) >= 7:
				if self.is_numeric(file_name_parts[5]) and len(file_name_parts[5]) == 8:
					jsonFileEntry['file_name_date'] = file_name_parts[5]
				else:
					jsonFileEntry['file_name_date'] = ""
				
				if self.is_numeric(file_name_parts[6]) and len(file_name_parts[6]) == 6:
					jsonFileEntry['file_name_time'] = file_name_parts[6]
				else:
					jsonFileEntry['file_name_time'] = ""
			else:
				jsonFileEntry['file_name_date'] = ""
				jsonFileEntry['file_name_time'] = ""
			
			if jsonFileEntry['file_name_date'] != "":
				jsonFileEntry['file_name_ts'] = datetime.datetime.strptime(jsonFileEntry['file_name_date'] + " " + jsonFileEntry['file_name_time'],"%Y%m%d %H%M%S").strftime("%Y-%m-%d %H:%M:%S")
			else:
				jsonFileEntry['file_name_ts'] = ""
			
			return True
		else:
			pass
			
		return False

	def parse_log_file(self, input_logfile):
		print "\nParse log file..."
		
		is_header 		= True
		f_input_log_file = open(input_logfile, 'r')
		for line_of_text in f_input_log_file:
			#remove trailing new line, tabs, colon followed by a space and any space longer than 1 with a single space
			line_of_text_formatted = re.sub(' +',' ',line_of_text.rstrip().replace("\n"," ").replace("\t"," ").replace(": "," "))
			line_parts = re.split(" ",line_of_text_formatted)

			if is_header:
				is_header = self.parse_header(line_parts)
			else:
				if self.parse_file_entry(line_parts):
					self.save_filelist_entry()

		f_input_log_file.close()
		
		for r in db.execute("SELECT COUNT(*) FROM DIRMON_FILELIST"):
			print '--> Rows parsed into DIRMON_FILELIST: %s' % r[0]
		
	# ====================================================================
	# WRITE TO FILE FUNCTIONS
	# ====================================================================
	def	save_filelist_to_file(self, output_base_name):
		print "\nSave File List to file"
		
		output_file_name = output_base_name + "_FILELIST.csv"
		csv_file = open(output_file_name, 'wb')
		csv_file.truncate()

		headers = "loop_no;loop_ts;host_name;file_name;file_ext;file_size;file_ts;filename_ts\n"
		csv_file.write(headers)
		
		rc = 0
		for table_row in db.execute('SELECT * FROM DIRMON_FILELIST' ):
			line = ( "%s;%s;%s;%s;%s;%s;%s;%s\n"%(table_row[0],table_row[1],table_row[2],table_row[3],table_row[4],table_row[5],table_row[6],table_row[7]))
			csv_file.write(line)
			rc = rc + 1
			
		csv_file.close()
		print "--> Rows written to " + output_file_name + ": " + str(rc)
		
	def	save_filesummary_to_file(self, output_base_name):
		print "\nSave File Summary to file"
		
		output_file_name = output_base_name + "_FILESUMMARY.csv"
		csv_file = open(output_file_name, 'wb')
		csv_file.truncate()

		headers = "file_name;loop_no_first;loop_no_last;first_seen_ts;last_seen_ts;age\n"
		csv_file.write(headers)
		
		rc = 0
		for table_row in db.execute('SELECT file_name, loop_no_first, loop_no_last, first_seen_ts, last_seen_ts, age FROM DIRMON_FILE_SUMMARY' ):
			line =  ( "%s;%s;%s;%s;%s;%s\n"
					%
						(
						  table_row[0]
						, table_row[1]
						, table_row[2]
						, table_row[3]
						, table_row[4]
						, int ( (datetime.datetime.strptime(table_row[4], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(table_row[3], "%Y-%m-%d %H:%M:%S")).total_seconds() )
						)
					)
			csv_file.write(line)
			rc = rc + 1
			
		csv_file.close()
		print "--> Rows written to " + output_file_name + ": " + str(rc)
		
	def	save_loopsummary_to_file(self, output_base_name):
		print "\nSave Loop Summary to file"
		
		output_file_name = output_base_name + "_LOOPSUMMARY.csv"
		csv_file = open(output_file_name, 'wb')
		csv_file.truncate()

		headers = "loop_no;loop_ts;host_name;ob_file_count;ob_file_size;ob_file_oldest_ts;ob_file_latest_ts;ob_file_oldest_age;ob_file_latest_age;all_file_count;all_file_size\n"
		csv_file.write(headers)
		
		rc = 0
		for table_row in db.execute('SELECT loop_no, loop_ts, host_name, ob_file_count, ob_file_size, ob_file_oldest_ts, ob_file_latest_ts, all_file_count, all_file_size FROM DIRMON_LOOP_SUMMARY'):
			line =  ( "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
					%
						(
						  table_row[0]
						, table_row[1]
						, table_row[2]
						, table_row[3]
						, table_row[4]
						, table_row[5]
						, table_row[6]
						, int ( (datetime.datetime.strptime(table_row[1], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(table_row[5], "%Y-%m-%d %H:%M:%S")).total_seconds() )
						, int ( (datetime.datetime.strptime(table_row[1], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(table_row[6], "%Y-%m-%d %H:%M:%S")).total_seconds() )
						, table_row[7]
						, table_row[8]
						)
					)
			csv_file.write(line)
			rc = rc + 1
			
		csv_file.close()
		print "--> Rows written to " + output_file_name + ": " + str(rc)
	
	# ====================================================================
	# HTML FUNCTIONS
	# ====================================================================
	def	save_filesummary_to_html(self, output_base_name):
		print "\nSave File Summary to html"
		
		f_html_template_file = open("html_template_new.html", 'r')
		output_file_name = output_base_name + "_FILESUMMARY.html"
		f_html_file = open(output_file_name, 'wb')
		f_html_file.truncate()

		for html_line_of_text in f_html_template_file:
			if html_line_of_text[0:2] != '$$':
				f_html_file.write(html_line_of_text)
			else:
				print html_line_of_text
				line_var = html_line_of_text.replace("$$","").replace("\n","").replace(" ","")
				print line_var
				if line_var == "DATATABLE_HAEDER":
					header = "['file_name','','age']\n"
					f_html_file.write(header)
				elif line_var == "DATATABLE_DATA":

					for table_row in db.execute('SELECT file_name, loop_no_first, loop_no_last, first_seen_ts, last_seen_ts FROM DIRMON_FILE_SUMMARY' ):				
						line = ( ",['%s',%s,%s]\n" 
						        %
									(
									  table_row[0]
									, table_row[1]
									, int ( (datetime.datetime.strptime(table_row[4], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(table_row[3], "%Y-%m-%d %H:%M:%S")).total_seconds() )
									)
								)
						f_html_file.write(line)
				else:
					print "Variable '%s' is not recognized" % line_var
		

		f_html_file.close()
		f_html_template_file.close()
		print "--> done"
	
	# ====================================================================
	# MAIN FUNCTION
	# ====================================================================
	def parseFile(self, input_logfile, output_base_name):

		#parse the log file
		self.parse_log_file(input_logfile)
		
		#file parsed and loaded into table, now process the data
		self.process_file_summary()
		self.process_loop_summary()
		
		#Data processed, now spool to CSV files
		self.save_filelist_to_file(output_base_name)
		self.save_filesummary_to_file(output_base_name)
		self.save_loopsummary_to_file(output_base_name)
		
		#Generate HTML files
		self.save_filesummary_to_html(output_base_name)
		
		print "Done..."