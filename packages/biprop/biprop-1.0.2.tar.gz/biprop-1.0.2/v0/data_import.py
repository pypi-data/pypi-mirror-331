# -*- coding: utf-8 -*-
"""
data_import.py imports the 2023 Swiss National Council Election data from the official JSON file.
Copyright (C) 2024  Talin Herold
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas
import urllib


cantons = [{'abb': 'ZH', 'seats': 36, 'bfs_nr':  1, 'name': 'Zürich',},
           {'abb': 'BE', 'seats': 24, 'bfs_nr':  2, 'name': 'Bern',},
           {'abb': 'LU', 'seats':  9, 'bfs_nr':  3, 'name': 'Luzern',},
           {'abb': 'UR', 'seats':  1, 'bfs_nr':  4, 'name': 'Uri',},
           {'abb': 'SZ', 'seats':  4, 'bfs_nr':  5, 'name': 'Schwyz',},
           {'abb': 'OW', 'seats':  1, 'bfs_nr':  6, 'name': 'Obwalden',},
           {'abb': 'NW', 'seats':  1, 'bfs_nr':  7, 'name': 'Nidwalden',},
           {'abb': 'GL', 'seats':  1, 'bfs_nr':  8, 'name': 'Glarus',},
           {'abb': 'ZG', 'seats':  3, 'bfs_nr':  9, 'name': 'Zug',},
           {'abb': 'FR', 'seats':  7, 'bfs_nr': 10, 'name': 'Fribourg',},
           {'abb': 'SO', 'seats':  6, 'bfs_nr': 11, 'name': 'Solothurn',},
           {'abb': 'BS', 'seats':  4, 'bfs_nr': 12, 'name': 'Basel-Stadt',},
           {'abb': 'BL', 'seats':  7, 'bfs_nr': 13, 'name': 'Basel-Landschaft',},
           {'abb': 'SH', 'seats':  2, 'bfs_nr': 14, 'name': 'Schaffhausen',},
           {'abb': 'AR', 'seats':  1, 'bfs_nr': 15, 'name': 'Appenzell Ausserrhoden',},
           {'abb': 'AI', 'seats':  1, 'bfs_nr': 16, 'name': 'Appenzell Innerrhoden',},
           {'abb': 'SG', 'seats': 12, 'bfs_nr': 17, 'name': 'St. Gallen',},
           {'abb': 'GR', 'seats':  5, 'bfs_nr': 18, 'name': 'Graubünden',},
           {'abb': 'AG', 'seats': 16, 'bfs_nr': 19, 'name': 'Aargau',},
           {'abb': 'TG', 'seats':  6, 'bfs_nr': 20, 'name': 'Thurgau',},
           {'abb': 'TI', 'seats':  8, 'bfs_nr': 21, 'name': 'Ticino',},
           {'abb': 'VD', 'seats': 19, 'bfs_nr': 22, 'name': 'Vaud',},
           {'abb': 'VS', 'seats':  8, 'bfs_nr': 23, 'name': 'Valais',},
           {'abb': 'NE', 'seats':  4, 'bfs_nr': 24, 'name': 'Neuchâtel',},
           {'abb': 'GE', 'seats': 12, 'bfs_nr': 25, 'name': 'Genève',},
           {'abb': 'JU', 'seats':  2, 'bfs_nr': 26, 'name': 'Jura',},]


parties = {'SVP'  : { 1: 'A1',
                      2: 'A1',
                      3: 'A1',
                      4: 1,
                      5: 'A1',
                      6: 2,
                      7: 1,
                      8: 2,
                      9: 'C2',
                     10: 'A1',
                     11: 'B1',
                     12: 'C1',
                     13: 'A2',
                     14: 'A1',
                     15: 3,
                     16: 2,
                     17: 1,
                     18: 'B1',
                     19: 'A1',
                     20: [1, 14],
                     21: 'B2',
                     22: 'C1',
                     23: [4, 5, 6, 15, 16, 17, 18],
                     24: 'C1',
                     25: 'A3',
                     26: 'C2',},
           'FDP'  : { 1: 'A2',
                      2: 'A2',
                      3: 'C2',
                      5: [2, 15, 16, 17, 18, 25, 26],
                      6: 1,
                      7: 3,
                      9: 'C1',
                     10: [3, 13],
                     11: [1, 2, 3, 4],
                     12: [1, 5, 21],
                     13: 'A1',
                     14: 'A2',
                     15: 2,
                     17: [12, 13, 14, 15, 16],
                     18: 'A1',
                     19: 'A2',
                     20: 'B1',
                     21: [5, 15, 18],
                     22: 'C2',
                     23: [8, 9, 10, 11, 12, 13],
                     24: [1, 2],
                     25: 'A2',
                     26: 'C1',},
           'SP'   : { 1: 'B1',
                      2: 'B1',
                      3: 'B1',
                      5: [9, 10, 12],
                      8: 3,
                      9: 'A2',
                     10: 'D1',
                     11: 'D2',
                     12: 'B1',
                     13: 'B1',
                     14: 'B1',
                     17: 'C1',
                     18: 'C1',
                     19: 'B1',
                     20: 'C2',
                     21: 'A1',
                     22: 'B2',
                     23: 'B1',
                     24: 'B1',
                     25: 'D2',
                     26: 'A1',},
           'GRÜNE': { 1: 'B2',
                      2: 'B2',
                      3: 'B2',
                      5: [23, 24],
                      9: 'A1',
                     10: 'D2',
                     11: 'D1',
                     12: [7, 16],
                     13: 'B2',
                     14: 'B2',
                     17: 'C2',
                     18: 'C2',
                     19: 'B2',
                     20: 'C1',
                     21: 'A2',
                     22: 'B1',
                     23: 'B2',
                     24: 'B2',
                     25: 'D1',
                     26: 'A2',},
           'GLP'  : { 1: 'C1',
                      2: 'C2',
                      3: 'B3',
                      5: 'C2',
                      9: 'B2',
                     10: 'C1',
                     11: 'C2',
                     12: 'A4',
                     13: 'C3',
                     14: 'C1',
                     17: 'C3',
                     18: 'C3',
                     19: 'B3',
                     20: 'C3',
                     21: [8, 23],
                     22: [10, 12, 14],
                     23: [34, 35],
                     24: 'D1',
                     25: [3, 14, 18, 25, 27],
                     26: [15, 16],},
           'Mitte': { 1: 'C2',
                      2: 'C1',
                      3: 'C1',
                      4: 2,
                      5: 'C1',
                      7: 2,
                      8: 4,
                      9: 'B1',
                     10: 'C2',
                     11: 'C1',
                     12: 'A3',
                     13: 'C2',
                     14: 8,
                     15: 1,
                     16: 1,
                     17: 'B1',
                     18: 'A2',
                     19: 'C1',
                     20: 'B3',
                     21: 'E1',
                     22: 'A1',
                     23: [1, 2, 7, 27, 28, 29, 30, 31],
                     24: 11,
                     25: 'A1',
                     26: 'B1',},
           'EVP'  : { 1: 'D1',
                      2: 'C3',
                      3: 20,
                      5: 22,
                      9: 14,
                     10: 12,
                     11: 28,
                     12: 3,
                     13: 'C1',
                     14: 9,
                     17: 'B2',
                     18: 9,
                     19: 'C2',
                     20: 'B2',
                     22: 22,
                     24: 15,
                     25: 19,   # list 19 is shared between EVP and EDU.
                     26: 14,}, # I attributed it to the EVP instead of the
           'EDU'  : { 1: 'E1', # EDU because (1) EVP's name shows up first
                      2: 'D1', # in the list's name and (2) SRF also attri-
                     10: 8,    # butes this list to the EVP.
                     12: 8,
                     13: 12,
                     14: 7,
                     17: 23,
                     18: 2,
                     19: 45,
                     20: 'A1',
                     22: 17,
                     24: 16,},
           'CSP'  : { 9: 9,
                     10: 4,},
           'Pirat': { 1: 'D2',
                      2: 33,
                     19: 46,
                     22: 2,},
           'AL'   : { 1: 8,},
           'MASS' : { 1: 33,
                      2: 36,
                      3: 39,
                      5: 27,
                     11: 29,
                     12: 23,
                     14: 15,
                     17: 28,
                     19: 48,
                     20: 33,},
           'SD'   : { 1: 37,
                      2: 34,
                      3: 48,
                     17: 29,},
           'Aufr' : { 1: 38,
                      2: 37,
                      9: 8,
                     13: 8,
                     17: 27,
                     20: 3,},
           'PdA'  : { 1: 41,
                     12: 10,
                     19: 49,
                     22: 3,
                     23: 36,
                     24: 5,},
           'BastA': {12: [13, 22],},
           'LDP'  : {12: [2, 18, 28],},
           'Lega' : {21: 'B1',},
           'EaG'  : {22: 19,
                     25: [2, 7, 12, 16, 17],},
           'Sol'  : {24: 8,},
           'MCG'  : {25: 'A4',},
           'Pfleg': { 1: 42,
                      5: 14},
           'Avant': {21: 2},
           'Valli': {21: 11},
           'H-ETH': {21: 20,
                     26: 17},
           'Vielf': { 5: 11},
           'JUTZI': { 2: 35},
           'BSLS' : { 2: 38},
           'Norm' : { 2: 39},
           'Più'  : {21: 21},
           'No UE': {21: 13},
           'SPP'  : { 1: 32},
           'LP'   : { 1: 36},
           'gAusg': { 1: 44},
           'WiM'  : { 1: 43},
           'Eth-U': { 1: 40},
           'Libté': {25: 21},
           "d'abo": {25: 23},
           'Freie': { 5: 13,
                     17: 26,
                     18: 19,},
           'Libre': {22: 5},
           'Rest' : { 3: [22, 23, 40],
                      4: 99,
                      8: [1, 99],
                      9: [23, 34],
                     10: [21, 22],
                     12: 12,
                     13: 11,
                     15: 99,
                     16: 99,
                     19: [47, 50, 51, 52],}}


party_replacements = {'CVP': 'Mitte',
                      'LPS': 'FDP',}



def import_raw_data(source, destination):
    """
    Downloads a file from `source` and saves it under `destination`. Returns
    the path to the new file and any messages passed on from
    urllib.request.urlretrieve. This function is equivalent to
        >>> import urllib
        >>> path, message = urllib.request.urlretrieve(source, destination)
    For more information, see the urlretrieve-documentation.

    """
    path, message = urllib.request.urlretrieve(source, destination)
    # print(message)
    # print(path)
    return path, message


def load_json(filename):
    """
    Uses pandas to load a json-file and returns a list. This function is
    equivalent to
        >>> import pandas
        >>> json_file = pandas.read_json(filename, typ='series')
    For more information, see the pandas.read_json-documentation.

    """
    results = pandas.read_json(filename, typ='series')
    return results


def get_party_dict(meta_file, replacements=party_replacements):
    metadata = pandas.read_json(meta_file, typ='series')['parteien']
    party_dict = {}
    for party in metadata:
        print(party['partei_bezeichnung_kurz'][0]['text'],
              party['parteigruppen_bezeichnung_kurz'][0]['text'],
              party['parteipolitische_lager_bezeichnung_kurz'][0]['text'], sep='    ')
        party_dict[party['partei_id']] = party['partei_bezeichnung_kurz'][0]['text']
    print(party_dict)


def test_parties_old(parties, votes, canton):
    canton_votes = votes.loc[votes['kanton_nummer']==canton]
    used_lists = []
    for party, lists in parties.items():
        if canton in lists:
            lists = lists[canton]
            print(party+'\n'+len(party)*'-')
            for nr in lists:
                print(canton_votes.loc[canton_votes['liste_nummer_bfs']==nr].iloc[0,4])
                used_lists.append(nr)
            print('\n')
    print('Not used\n--------')
    print(canton_votes.loc[~canton_votes['liste_nummer_bfs'].isin(used_lists)]['liste_bezeichnung'])
    print('\n')


def test_parties(parties, votes, canton):
    canton_votes = votes.loc[votes['kanton_nummer']==canton]
    used_lists = []
    
    # parties = {'FDP':   parties['FDP'],
    #            'Mitte': parties['Mitte']}
    # iterate through parties
    for party, lists in parties.items():
        # only proceed if party runs in given canton
        if canton in lists:
            lists = lists[canton]
            print(party+'\n'+len(party)*'-')
            
            # Find all sublists if lists are given via sublist connection
            if type(lists) == str:
                print(canton_votes.loc[canton_votes['liste_unterlistenverbindung']
                                       ==lists]['liste_bezeichnung'])
                used_lists.append(lists)
            
            # Find all lists if lists are given as list of lists
            elif type(lists) == list:
                for list_nr in lists:
                    print(canton_votes.loc[canton_votes['liste_nummer_bfs']==list_nr].iloc[0,4])
                    used_lists.append(list_nr)
            
            # Find list if list is given as single list number
            elif type(lists) == int:
                print(canton_votes.loc[canton_votes['liste_nummer_bfs']==lists]['liste_bezeichnung'])
                used_lists.append(lists)
            
            # Raise KeyError if lists is not valid
            else:
                raise KeyError(f'{lists} of type {type(lists)} is not a valid list specification!')
            print('\n')
    
    # Find and display the not used lists
    print('Not used\n--------')
    print(canton_votes.loc[(~canton_votes['liste_nummer_bfs'].isin(used_lists))
                            &(~canton_votes['liste_unterlistenverbindung'
                                            ].isin(used_lists))][['liste_bezeichnung',
                                                                'liste_nummer_bfs']])
    print('\n')


def get_votes(list_votes, parties=parties, cantons=cantons,
              fuse=None, return_seats=True, return_party_names=True,
              return_canton_names=True):
    """
    Converts a pandas dataframe or a (path pointing to a) JSON-file into a votes-
    array.

    Parameters
    ----------
    list_votes : pandas.DataFrame or str
        A pandas dataframe or a string containing the path of a JSON-file.
    parties : dictionary
        A dictionary of all parties and their lists. Each key-value pair should
        correspond to one party. The key should be the name of the party, the value
        should be another dictionary. In this dictionary, ever key-value pair
        should correspond to a canton. The keys should be the BFS numbers of the
        cantons and the values the lists that the given party has in the given
        canton. These lists can either be a string containing the sublist number,
        a single integer containing the list number or a list of integers
        containing the numbers of all lists of that party in that canton.
    cantons : list
        List containing additional informations about the cantons. Each item
        should be a dictionary and corresponds to one canton. This dictionary must
        contain its number of seats in the parliament under the key 'seats'. It
        should also contain its abbreviation under the key 'abb'.
    fuse : list of lists, optional
        Fuse gives you the ability to treat multiple parties as one. For example:
            fuse = [['party_a', 'party_b', 'party_c'], ['party_d', 'party_e']]
        treats the parties 'party_a', 'party_b' and 'party_c' as just one and
        'party_d' and 'party_e' also as just one party. 'party_i' must be a key
        of `parties`. The default is None.
    return_seats : bool, optional
        If true, the function also returns an array containing the number of seats
        each party received in each canton according to the Hagenbach-Bischoff
        system. The default is True.
    return_party_names : bool, optional
        If true, the function also returns a list where the i'th item is the name
        of the party corresponding to the i'th row of `votes`. The default is True.
    return_canton_names : bool or str, optional
        If true (or a non-empty string), the function also returns a list where
        the j'th item is the name of the canton corresponding to the j'th column
        of `votes`. If it is a non-empty string, the name of the i'th canton is set
        to `cantons[i][return_canton_names]`. Otherwise it is set to
        `cantons[i]['abb']`. The default is True.

    Returns
    -------
    votes: numpy.ndarray
        2D array containing the votes for each party in each canton. The i'th row
        corresponds to the votes for the i'th party and the j'th column corresponds
        to the votes casted in the j'th canton.
    seats_arr: numpy.ndarray (returned only if `return_seats` is True)
        2D array containing the number of seats the Hagenbach-Bischoff method
        apportioned to each party in each canton. The number i'th row and j'th
        column of `seats_arr` corresponds to the number of seats the i'th party
        won in the j'th canton.
    party_names: list (returned only if `return_party_names` is True)
        A list whose i'th item is the name of the party that corresponds to the
        i'th row of `votes`.
    canton_names : list (returned only if `bool(return_party_names)` is True)
        A list whose j'th item is the name of the canton that corresponds to the
        j'th column of `votes`.

    """
    # define important variables/lists/arrays for later
    NoC = len(cantons)
    NoP = len(parties)
    votes = np.zeros((NoP, NoC), dtype=float)
    if return_seats:
        seats_arr = np.zeros_like(votes, dtype=int)
    party_names = []
    
    # if list_votes is given as a path to a json_file, import it
    if type(list_votes) == str:
        list_votes = pandas.DataFrame(load_json(list_votes)['level_kantone'])
    elif type(list_votes) != pandas.DataFrame:
        raise TypeError("'list_votes' needs to be a pandas DataFrame or a datapath pointing to a JSON-file.")
    
    # if return_canton_names, get canton_names list
    if return_canton_names:
        if type(return_canton_names) == bool:
            return_canton_names = 'abb'
        canton_names = [canton[return_canton_names] for canton in cantons]
        return_canton_names = True
    
    # define a dictionary that maps each bfs-number to a column index in votes
    canton_indices = {}
    for n, canton in enumerate(cantons):
        canton_indices[canton['bfs_nr']] = n
    
    # iterate through all parties in parties
    for party_index, (party_name, party) in enumerate(parties.items()):
        party_names.append(party_name) # add party name to the party_names-list
        
        # iterate through all cantons in which the party runs
        for canton, lists in party.items():
            # set initial values for total votes and seats (in that canton)
            tot_votes = 0
            if return_seats:
                seats = 0
            
            # if type(lists) is str, use the "unterlistenverbindung" to obtain votes/seats
            if type(lists)==str:
                tot_votes = np.sum(list_votes.loc[(list_votes[
                    'liste_unterlistenverbindung']==lists) & (list_votes[
                    'kanton_nummer']==canton)]['stimmen_liste'])
                if return_seats:
                    seats = np.sum(list_votes.loc[(list_votes[
                        'liste_unterlistenverbindung']==lists) & (list_votes[
                        'kanton_nummer']==canton)]['anzahl_gewaehlte'])
            # if type(lists) is int, obtain votes/seats over the list number
            elif type(lists)==int:
                tot_votes = np.sum(list_votes.loc[(list_votes[
                    'liste_nummer_bfs']==lists) & (list_votes['kanton_nummer']
                    ==canton)]['stimmen_liste'])
                if return_seats:
                    seats = np.sum(list_votes.loc[(list_votes[
                        'liste_nummer_bfs']==lists) & (list_votes[
                        'kanton_nummer']==canton)]['anzahl_gewaehlte'])
            # if lists is a list/array of list numbers, sum over all list with right number
            elif type(lists) in (list, np.ndarray):
                tot_votes = np.sum(list_votes.loc[(list_votes[
                    'liste_nummer_bfs'].isin(lists)) & (list_votes[
                    'kanton_nummer']==canton)]['stimmen_liste'])
                if return_seats:
                    seats = np.sum(list_votes.loc[(list_votes[
                        'liste_nummer_bfs'].isin(lists)) & (list_votes[
                        'kanton_nummer']==canton)]['anzahl_gewaehlte'])
            
            # divide tot_votes by number of seats in that canton
            tot_votes /= cantons[canton_indices[canton]]['seats']
            # write tot_votes (seats) into votes (seats_arr) array
            votes[party_index, canton_indices[canton]] = tot_votes
            if return_seats:
                seats_arr[party_index, canton_indices[canton]] = seats
            # if party_name in ('SVP', 'SD', 'MASS'):
            #     print(f'{party_name:<7}{cantons[canton_indices[canton]]["abb"]}: {tot_votes}')
    
    # the following code merges different rows of the votes array if demanded by fuse
    if fuse != None:
        # define lists for new indices and names
        new_indices = []
        party_names_new = []
        next_index = 0 # the nextlowest unoccupied index
        fusion_indices = [None for i in fuse] # new index of the parties in fusion[n]
        
        # iterate through all parties
        for i, party in enumerate(party_names):
            assigned = False # marks that this party does not yet have new index
            # iterate through all lists in fusion to check if current party should be fused
            for n, fusion in enumerate(fuse):
                if party in fusion:
                    # if party is in fusion and this fusion does not yet have an index:
                    if fusion_indices[n] == None:
                        new_indices.append(next_index) # update new party index
                        fusion_indices[n] = next_index # update index of fusion
                        party_names_new.append(fusion[0]) # update new party names
                        next_index += 1 # increment index
                    else: # if index is in fusion and fusion has an index
                        new_indices.append(fusion_indices[n]) # assign that index
                    assigned = True # party has new index
                    break
            # if the party does not yet have a new index, give it the next free index
            if not assigned:
                new_indices.append(next_index)
                party_names_new.append(party)
                next_index += 1
        NoP = max(new_indices)+1 # find the new number of parties
        fused_votes = np.zeros((NoP, NoC), dtype=float) # new votes array
        if return_seats:
            fused_seats = np.zeros_like(fused_votes) # new seats array
        # iterate through new_indices to assign the rows of votes to the fused_votes
        for old_index, new_index in enumerate(new_indices):
            fused_votes[new_index] += votes[old_index]
            if return_seats:
                fused_seats[new_index] += seats_arr[old_index]
        # rename arrays and lists
        votes = fused_votes
        if return_seats:
            seats_arr = fused_seats
        party_names = party_names_new
    
    match (return_seats, return_party_names, return_canton_names):
        case (True, True, True):
            return votes, seats_arr, party_names, canton_names
        case (True, True, False):
            return votes, seats_arr, party_names
        case (True, False, True):
            return votes, seats_arr, canton_names
        case (True, False, False):
            return votes, seats_arr
        case (False, True, True):
            return votes, party_names, canton_names
        case (False, True, False):
            return votes, party_names
        case (False, False, True):
            return votes, canton_names
        case _:
            return votes


if __name__=='__main__':
    
    ########## URLs and filenames of the raw data #############################
    # url and filename of the candidates-json
    # url = 'https://ogd-static.voteinfo-app.ch/v4/ogd/sd-t-17.02-NRW2023-kandidierende.json'
    # filename = 'Election_Results\\results_candidates.json'
    # # import_raw_data(url, filename)
    
    # url and filename of the parties-json
    # url = 'https://ogd-static.voteinfo-app.ch/v4/ogd/sd-t-17.02-NRW2023-parteien.json'
    # filename = 'Election_Results\\results_parties.json'
    # # import_raw_data(url, filename)
    
    # url and filename of the lists-json
    url = 'https://ogd-static.voteinfo-app.ch/v4/ogd/sd-t-17.02-NRW2023-listen.json'
    filename = 'Election_Results\\results_lists.json'
    # import_raw_data(url, filename)
    
    # url and filename of the metadata-json
    # meta_url = 'https://ogd-static.voteinfo-app.ch/v4/ogd/sd-t-17.02-NRW2023-metadaten.json'
    # meta_filename = 'Election_Results\\metadata.json'
    # # import_raw_data(meta_url, filename)
    ###########################################################################
    
    
    ########## PARTIES STRUCTURE ##############################################
    ct_nr = 1
    test = True
    
    votes = pandas.DataFrame(load_json(filename)['level_kantone'])
    zh = votes.loc[votes['kanton_nummer'] == ct_nr]
    sublists = zh['liste_unterlistenverbindung'].unique()
    sublists.sort()
    
    if not test:
        for sublist_con in sublists:
            print(sublist_con+'\n'+len(sublist_con)*'-')
            print(zh.loc[zh['liste_unterlistenverbindung'] == sublist_con][
                            ['liste_bezeichnung', 'liste_nummer_bfs']])
            print('\n')
    else:
        test_parties(parties, votes, ct_nr)
        # for i in range(1, 27):
        #     test_parties(parties, votes, i)
        #     input()
    ###########################################################################
    
    # list_votes = pandas.DataFrame(load_json(filename)['level_kantone'])
    
    # votes, p_ind = get_votes(list_votes, fuse=None)
    # print(votes[0:2, 0:3])
    # votes, p_ind = get_votes(list_votes, fuse=[['SVP', 'FDP']])
    # print(votes[0:1, 0:3])
    
    print('\nend')