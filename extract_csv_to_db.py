#!/usr/bin/python
#encoding:UTF-8

import csv
import sys
import sqlite3

def main(args):
    
    if len(args) < 3:
        print 'Args: [csv_file] [table_name]'
        sys.exit(1)
    
    headers = ['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','LBH','LBA','LBD','WHH','WHA','WHD']
    
    # read in data
    f = open (args[1],'r')
    table_name = args[2]
    
    reader = csv.reader(f)
    h = reader.next()
    h_indices = [ h.index(x) for x in headers ]
        
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create table
    c.execute("CREATE TABLE IF NOT EXISTS %s (date text, home_team text, away_team text, fthg int, ftag int, ftr int, lbh real, lba real, lbd real, whh real, wha real, whd real)" % table_name)

    print 'read in data:'

    # write to db
    for row in reader:  
        print row
        c.execute("INSERT INTO "+table_name+" VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tuple(row))

    # Save (commit) the changes
    conn.commit()
    c.close()

if __name__=='__main__':
    main(sys.argv)
    


