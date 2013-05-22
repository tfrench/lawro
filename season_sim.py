#!/usr/bin/python
#encoding:UTF-8

'''
Simulate a season of EPL games

by Thomas French (thomas@sandtable.com)

To run the application:
$ python season_sim.py [table_name]

Arguments: table name from {EPL10_11, EPL11_12, EPL12_13}

Tested on python 2.7
Execution time is about 2/3 seconds.

Add a strategy by adding a new function that accepts a game
as an argument. 

A game is a list: [date, home_team, away_team, fthg, ftag, whh, wha, whd, lbh, lba, lbd]

The result should be one of [0,1,2], where
0 is home win
1 is away win
2 is a draw

Then add your strategy function name to the strategies dictionary, and run.
'''

import sys
import sqlite3
import random

import league_table_lib 

# globals
team_ranks = None

#
# Strategies
#

def uniform (game):
    return random.choice([0,1,2]),

def always_home (game):
    return 0,
def always_away (game):
    return 1,
def always_draw (game):
    return 2,

def heuristic (game):
    h_t=game[1] # home team
    a_t=game[2] # away team
    
    if team_ranks[h_t] >= 18: # bottom 3
        return 1, # away win
    elif team_ranks[h_t] > 4 and team_ranks[a_t] <= 4:
        return 1, # away win
    else:
        return 0, # default: home win

def william_hill (game):
    p=(1.0/game[5],1.0/game[6],1.0/game[7])
    
    if p[1] < p[0] > p[2]:
        return 0,
    elif p[0] < p[1] > p[2]:
        return 1,
    elif p[0] < p[2] > p[1]:
        return 2,
    else:
        return 0,

def ladbrokes (game):
    p=(1.0/game[8],1.0/game[9],1.0/game[10])
    
    if p[1] < p[0] > p[2]:
        return 0,
    elif p[0] < p[1] > p[2]:
        return 1,
    elif p[0] < p[2] > p[1]:
        return 2,
    else:
        return 0,

strategies = {
                'uniform' : uniform,
                'always_home' : always_home,
                'always_away' : always_away,
                'always_draw' : always_draw,
                'heuristic' : heuristic,
                'william_hill' : william_hill,
                'ladbrokes' : ladbrokes,
                }

#
# main
#

def main(args):
    global team_ranks
    
    if len(args) < 2:
        print 'Args: [table_name]'
        sys.exit(1)
    dbtable = args[1]
    print 'table: %s' % dbtable
    
    # db connection 
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # simulate season of games
    cursor.execute("SELECT count(*) from %s" % dbtable)
    total_games = int(cursor.fetchone()[0])
    print 'Total games: %s' % total_games
        
    # get dates in chronological order
    cursor.execute("SELECT distinct(date) from %s order by date ASC" % dbtable)
    rows = cursor.fetchall()
    dates = [ str(r[0]) for r in rows ]
    print 'Total play dates: %s' % len(dates)
    
    # MAIN LOOP 
    totals = {'H':0,'A':0,'D':0}
    
    # store results
    strategy_results = { k : 0 for k in strategies.keys()}
    
    games_played = 0
    
    # for each matchday
    for d in dates:
        cursor.execute("SELECT date, home_team, away_team, fthg, ftag, whh, wha, whd, lbh, lba, lbd from %s where date='%s'" % (dbtable, d))
        games = [ r for r in cursor.fetchall() ]
        
        league_table = league_table_lib.gen_league_table(cursor, dbtable, d)
        team_ranks = league_table_lib.gen_team_positions(league_table)
    
        # for each game
        for g in games:
            result = None
            if g[3] > g[4]:
                result = 0
                totals['H'] += 1
            elif g[3] < g[4]:
                result = 1
                totals['A'] += 1
            else:
                result = 2
                totals['D'] += 1
            
            for s in strategy_results.keys():
                r = strategies[s](g)
                
                # for each strategy make prediction
                if r[0] == result:
                    strategy_results[s] += 1
            
            games_played += 1
            
            if games_played % 50 == 0:
                print 'Games played: %s' % games_played
                    
    # close db
    conn.commit()
    cursor.close()
    
    # print results
    print 'Season counts: %s' % totals
    
    print '\nResults:'
    print 'rank, strategy, correct results, percentage'
    
    sorted_res = sorted(strategy_results, key=lambda x : strategy_results[x], reverse=True)
    for i,x in enumerate(sorted_res):
        print (i+1), x, strategy_results[x], float(strategy_results[x])/float(total_games)
    
if __name__=='__main__':
    main(sys.argv)
