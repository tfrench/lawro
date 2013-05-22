"""
League table functions
"""

def gen_team_positions(table):
    positions = {}
    for i in range(len(table)):
        positions[table[i][0]]=i+1
    return positions

def gen_league_table(cursor, dbtable, date):
    '''
    Generate league table for a given date
    '''
    # get teams 
    cursor.execute("SELECT distinct(home_team) FROM %s" % dbtable)
    r = cursor.fetchall()   
    teams = []
    for row in r:
        teams.append(row[0])

    league_table = []

    for t in teams:     
        # games played
        cursor.execute("SELECT count(*) FROM "+dbtable+" WHERE (home_team=='"+t+"' or away_team=='"+t+"') and date < "+ str(date))
        n = cursor.fetchone()[0]
            
        pts = 0
    
        # results

        # home wins
        cursor.execute("SELECT count(*) FROM %s WHERE home_team=='%s'and ftr=='H' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_h_w = r[0] if r[0] else 0
        pts += 3*r_h_w
    
        # home losses
        cursor.execute("SELECT count(*) FROM %s WHERE home_team=='%s'and ftr=='A' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_h_l = r[0] if r[0] else 0
    
        # home draws
        cursor.execute("SELECT count(*) FROM %s WHERE home_team=='%s'and ftr=='D' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_h_d = r[0] if r[0] else 0
        pts += r_h_d
    
        # away wins
        cursor.execute("SELECT count(*) FROM %s WHERE away_team=='%s'and ftr=='A' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_a_w = r[0] if r[0] else 0
        pts += 3*r_a_w
        
        # away losses
        cursor.execute("SELECT count(*) FROM %s WHERE away_team=='%s'and ftr=='H' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_a_l = r[0] if r[0] else 0
    
        # away draws
        cursor.execute("SELECT count(*) FROM %s WHERE away_team=='%s'and ftr=='D' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_a_d = r[0] if r[0] else 0
        pts += r_a_d

        # goals

        # home
        # for
        cursor.execute("SELECT sum(fthg) FROM %s WHERE home_team=='%s' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_h_f = r[0] if r[0] else 0

        # against
        cursor.execute("SELECT sum(ftag) FROM %s WHERE home_team=='%s' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_h_a = r[0] if r[0] else 0

        # away
        # for
        cursor.execute("SELECT sum(ftag) FROM %s WHERE away_team=='%s' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_a_f = r[0] if r[0] else 0

        # against
        cursor.execute("SELECT sum(fthg) FROM %s WHERE away_team=='%s' and date < %s" % (dbtable,t,date))
        r = cursor.fetchone()
        r_a_a = r[0] if r[0] else 0
    
        # goal difference
        total_for = r_h_f+r_a_f
        total_against = r_h_a+r_a_a
        gd = (total_for) - (total_against)
            
        wins = r_h_w+r_a_w
        draws = r_h_d+r_a_d
        losses = r_h_l+r_a_l
    
        league_table.append([str(t), n, r_h_w, r_h_d, r_h_l, r_h_f, r_h_a, 
                            r_a_w, r_a_d, r_a_l, r_a_f, r_a_a, 
                            wins, draws, losses, gd, pts])
                        
    # sort
    s = sorted(league_table, key=lambda x: (x[-1],x[-2]), reverse=True)
    return s