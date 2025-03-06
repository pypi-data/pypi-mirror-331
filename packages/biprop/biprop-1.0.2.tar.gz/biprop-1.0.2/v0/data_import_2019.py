# -*- coding: utf-8 -*-
"""
data_import_2019.py imports the 2019 Swiss National Council Election data from the official Excel file.
Copyright (C) 2021  Talin Herold
"""

import pandas as pd
import numpy as np


""" First dimension of vote vectors correspont to parties, second to regions
"""

### Test numbers for testing ###
test1_seats_per_region  = np.array([7, 5, 8])

test1_data              = np.array([[123,  45, 815],
                                    [912, 714, 414],
                                    [312, 255, 215],])

test2_seats_per_region  = np.array([4, 5, 6])

test2_data              = np.array([[ 5100,  9800,  4500],
                                    [ 6000, 10000, 12000],
                                    [ 6300, 10200, 14400],])

test_region_names       = np.array(["Huntington Hill",
                                    "Pukelsdorf",
                                    "D'Hont Valley"])

test_party_names        = np.array(["Spotted Party",
                                    "Striped Party",
                                    "Checkered Party"])

def update_party_nr(pnr):
    key = []
    for n, i in enumerate(pnr):
        if not i in key:
            key.append(i)
        pnr[n] = key.index(i)
    return pnr
                


def assign_party_names(pnr, pna):
    pna_def = np.empty_like(pna)
    for n, i in enumerate(pna):
        pna_def[pnr[n]] = i
    return pna_def[0:(np.max(pnr)+1)]

def assign_canton_names(cnr, cna):
    names = ["" for i in range(np.max(cnr)+1)]
    for n, i in enumerate(cna):
        if i not in names:
            names[cnr[n]] = i
    return np.array(names, dtype=str)


def create_votes_array(proto_votes, pnr, cnr, cse, dtype=float):
    votes = np.zeros((np.max(pnr)+1, np.max(cnr)+1), dtype=dtype)
    for n, i in enumerate(proto_votes):
        votes[pnr[n], cnr[n]] += i
    for n, i in enumerate(cse):
        votes[:,n] /= i
    return votes


### Read table and store columns in 1D-arrays ###
table = pd.read_excel("Election_Results_2019\\Nationalratswahl 2019.xlsx")
canton_nr           = np.array(table[table.columns[ 0]][1:535],
                               dtype=np.int64)
canton_nr          -= 1 # start with 0 to allow using canton_nr as incices
proto_canton_name   = np.array(table[table.columns[ 1]][1:535],
                               dtype=str)
list_nr             = np.array(table[table.columns[ 2]][1:535],
                               dtype=np.int64)
list_nr_official    = np.array(table[table.columns[ 3]][1:535],
                               dtype=str)
list_name           = np.array(table[table.columns[ 4]][1:535],
                               dtype=str)
list_connection     = np.array(table[table.columns[ 5]][1:535],
                               dtype=str)
sublist_connection  = np.array(table[table.columns[ 6]][1:535],
                               dtype=str)
party_nr            = np.array(table[table.columns[ 7]][1:535],
                               dtype=np.int64)
party_nr           -= 1 # start with party number 0 to use list_nr as array indices
proto_party_name    = np.array(table[table.columns[ 8]][1:535],
                               dtype=str)
proto_votes         = np.array(table[table.columns[ 9]][1:535],
                               dtype=np.int64)
list_strength       = np.array(table[table.columns[10]][1:535],
                               dtype=float) # in percent
mandates            = np.array(table[table.columns[11]][1:535],
                               dtype=np.int64)

canton_seats        = np.array([35, 24,  9,  1,  4,
                                 1,  1,  1,  3,  7,
                                 6,  5,  7,  2,  1,
                                 1, 12,  5, 16,  6, 
                                 8, 19,  8,  4, 12,  2], dtype=np.int64)

update_party_nr(party_nr)
party_names = assign_party_names(party_nr, proto_party_name)
canton_names = assign_canton_names(canton_nr, proto_canton_name)

votes = create_votes_array(proto_votes, party_nr, canton_nr, canton_seats)

current_seats = create_votes_array(mandates, party_nr, canton_nr, [], np.int64)

if __name__=="__main__":
    
    print(np.sum(current_seats))
    print(current_seats[:,0])
#    # Übrige are index 11
#    ind = 11
#    print(party_names[ind])
#    for n, i in enumerate(party_nr):
#        if i == ind:
#            print(n+3)
#    print()
#    
#    print(np.sum(canton_seats))
#    
    print("end")