#!/usr/bin/env python3
# Copyright (C) 2016  Red Hat, Inc.
# Author: Eduard Cuba <xcubae00@stud.fit.vutbr.cz>
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.

import argparse
import os
import sys
import sqlite3
import datetime

def print_format(*args):
    print('{:>7} | {:<24}| {:<16} | {:<15}|{:^8} '.format(*args))

################################ INPUT PARSER #################################

#input argument parser
parser = argparse.ArgumentParser(description="Unified DNF software database utils")
parser.add_argument('-i', '--input', help='SW_DB path, default: ./sw_db.sqlite', default='./sw_db.sqlite')
args = parser.parse_args()

sw_db_path = args.input

#check path to sw_db file
if not os.path.isfile(sw_db_path):
    sys.stderr.write('Error: sw_db file not valid\n')
    exit(1)

#initialise SW DB
database = sqlite3.connect(sw_db_path)
cursor = database.cursor()

cursor.execute('SELECT * FROM TRANS')
transactions = cursor.fetchall()
print_format('ID',' Command Line',' Date and Time',' Action(s)', ' Altered')
print('-----------------------------------------------------------------------------')
for transaction in transactions[::-1]:
    output = [''] * 5
    output[0] = transaction[0]
    output[1] = (transaction[4])[:24]
    output[2] = str(datetime.datetime.fromtimestamp(int(transaction[1])))[:16]
    cursor.execute('SELECT state FROM TRANS_DATA WHERE T_ID = ?',(transaction[0],))
    all_actions = cursor.fetchall()
    altered = 0
    for action in all_actions:
        cursor.execute('SELECT description FROM STATE_TYPE WHERE id=?',(action[0],))
        action = cursor.fetchone()
        if action[0] != 'Installed' and action[0] != 'Updated':
            altered+=1
    output[4] = altered
    actions = list(set(all_actions))
    u_actions = []
    for action in actions:
        cursor.execute('SELECT description FROM STATE_TYPE WHERE id=?',(action[0],))
        action = cursor.fetchone()
        u_actions.append(action[0])
    if 'Updated' in u_actions:
        del u_actions[u_actions.index('Updated')]
    if 'Obsoleted' in u_actions:
        del u_actions[u_actions.index('Obsoleted')]
    if len(u_actions) == 1:
        output[3] = u_actions[0]
    else:
        u_actions = sorted(u_actions)
        for action in u_actions:
            if output[3] == '':
                output[3] = action[0]
            else:
                output[3] += ', '+action[0]

    print_format(*output)




#close connection
database.close()
