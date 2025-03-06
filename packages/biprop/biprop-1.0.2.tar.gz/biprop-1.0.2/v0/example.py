# -*- coding: utf-8 -*-
"""
example.py is a python module that demonstrates how to use biprop.py.
Copyright (C) 2024  Talin Herold
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas
import os
import biprop as biprop
import data_import
import data_import_2019
from data_import import cantons, parties


# defines the order in which the parties will be plotted
party_order = ['MASS', 'Aufr', 'Lega', 'EDU', 'SVP', 'MCG', 'FDP', 'BDP',
               'Mitte', 'EVP', 'GLP', 'Pirat', 'SP', 'GRÜNE', 'PdA']
# Define the party colors for the plots. Each color string should be one
# of the named matplotlib colors.
party_colors = {'MASS' : 'rebeccapurple',
                'Aufr' : 'mediumslateblue',
                'Lega' : 'fuchsia',
                'EDU'  : 'saddlebrown',
                'SVP'  : 'darkgreen',
                'MCG'  : 'dodgerblue',
                'FDP'  : 'mediumblue',
                'Mitte': 'darkorange',
                'EVP'  : 'gold',
                'GLP'  : 'greenyellow',
                'Pirat': 'goldenrod',
                'SP'   : 'red',
                'GRÜNE': 'limegreen',
                'PdA'  : 'mediumvioletred',
                'LDP'  : 'cyan',
                'BDP'  : 'coral',
                'Sol'  : 'pink',
                'AL'   : 'teal'}
# Used to rename some of the parties from the data_import_2019 as the
# 2019 data uses different names than the 2023 data.
party_rename = {'GPS'  : 'GRÜNE',
                'LPS'  : 'LDP',
                'PIR'  : 'Pirat',
                'FGA'  : 'AL',
                'CVP'  : 'Mitte',
                'Sol.' : 'Sol',
                'MCR'  : 'MCG',}


def plot_total_result(distributions, party_names, legend=None, save_fig=False,
                      colors=['tab:blue', 'tab:orange', 'tab:green',
                      'tab:red', 'tab:purple', 'tab:brown', 'tab:pink',
                      'tab:gray', 'tab:olive', 'tab:cyan']):
    """
    Plots a comparison of different distributions passed in the first argument.
    Makes a bar chart with a bar for every party-distribution combination.

    """
    NoD = len(distributions)
    if legend == None:
        legend = [i for i in range(NoD)]
        make_legend = False
    else:
        make_legend = True
    
    plt.figure(dpi=200)
    
    for n, dist in enumerate(distributions):
        for m, p_seats in enumerate(dist):
            if m==0:
                plt.barh(-m*(NoD+1)-n, p_seats.sum(), height=1, label=legend[n],
                         color=colors[n%len(colors)])
            else:
                plt.barh(-m*(NoD+1)-n, p_seats.sum(), height=1,
                         color=colors[n%len(colors)])
    
    plt.xticks(np.arange(0, plt.xlim()[-1], 1), minor=True)
    plt.xticks(np.arange(0, plt.xlim()[-1], 5), minor=False)
    plt.grid(axis='x', which='major', linewidth=1)
    plt.grid(axis='x', which='minor', linewidth=0.5)
    plt.yticks([-NoD/2-(NoD+1)*i for i in range(len(party_names))], party_names)
    if make_legend:
        plt.legend()
    plt.xlabel('Seats / Party strength ($0.5\%$)')
    plt.title('Seats by Party')
    if save_fig:
        plt.savefig(save_fig, bbox_inches='tight')
    plt.show()


def plot_parliament(distributions, dist_names, party_names,
                    colors=party_colors, save_fig=False):
    """
    Plots a comparison of the overall seat distribution of the different
    distributions passed in the first argument.

    """
    plt.figure(figsize=(8,4.5), dpi=200)
    
    for n, dist in enumerate(distributions):
        offset = 0
        for p_ind, p_seats in enumerate(dist):
            p_seats = p_seats.sum()
            if n==0:
                plt.barh(-n, p_seats, left=offset, label=party_names[p_ind],
                         color=colors[party_names[p_ind]])
            else:
                plt.barh(-n, p_seats, left=offset,
                         color=colors[party_names[p_ind]])
            offset += p_seats
    
    plt.xticks(np.arange(0, 201, 5), minor=True)
    plt.grid(axis='x', which='major', linewidth=1)
    plt.grid(axis='x', which='minor', linewidth=0.5)
    plt.yticks([-i for i in range(len(distributions))], dist_names,
               rotation=60)
    plt.xlabel('Seats')
    plt.title('National Council Membership')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncols=7)
    plt.margins(tight=True)
    if save_fig:
        plt.savefig(save_fig, bbox_inches='tight')
    plt.show()


def plot_canton(distributions, dist_names, party_names, region_names,
                regions='all', colors=party_colors, save_fig=False):
    """
    Plots a comparison of the seat distributions of a specified region/canton.
    
    """
    if regions == 'all':
        regions = region_names
    elif type(regions) == str:
        regions = [regions,]
    for region in regions:
        for n, r in enumerate(region_names):
            if region==r:
                region_index = n
                break
        plt.figure(figsize=(8, 4.5), dpi=200)
        
        for n, dist in enumerate(distributions):
            offset = 0
            for p_ind, p_seats in enumerate(dist):
                p_seats = p_seats[region_index]
                if n==0:
                    plt.barh(-n, p_seats, left=offset, label=party_names[p_ind],
                             color=colors[party_names[p_ind]])
                else:
                    plt.barh(-n, p_seats, left=offset,
                             color=colors[party_names[p_ind]])
                offset += p_seats
        
        plt.xticks(np.arange(0, offset+0.5, 1), minor=True)
        if offset <= 10:
            plt.xticks(np.arange(0, offset+0.5, 1))
        elif offset <= 20:
            plt.xticks(np.arange(0, offset+0.5, 2))
        else:
            plt.xticks(np.arange(0, offset+0.5, 5))
        plt.grid(axis='x', which='major', linewidth=1)
        plt.grid(axis='x', which='minor', linewidth=0.5)
        plt.yticks([-i for i in range(len(distributions))], dist_names,
                   rotation=60)
        plt.xlabel('Seats')
        plt.title(f'National Council Membership in {region}')
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncols=7)
        plt.margins(tight=True)
        if save_fig:
            plt.savefig(save_fig.rpartition('.')[0]+f'_{region}'
                        + save_fig.rpartition('.')[1] + save_fig.rpartition('.')[2],
                        bbox_inches='tight')
        plt.show()


def protected_winner_rounding(votes, rounding_method=np.round):
    """
    Defines and returns a rounding function that can be passed to
    biprop.proportional_apportionment and that guarantees that within
    every canton, the party with the most votes gets at least one seat.

    """
    # find the winner in each region and mark it with a one
    min_seats = np.zeros_like(votes, dtype=int)
    min_seats[np.argmax(votes, axis=0), range(len(votes[0]))] = 1
    # define a function that returns the provisional seats, except if a regional
    # winner has zero seats, then a one is returned instead
    def pwr(v):
        prov_seats = np.array(rounding_method(v), dtype=int)
        return np.where(min_seats>prov_seats, min_seats, prov_seats)
    # return protected_winner_rounding
    return pwr


if __name__=='__main__':
    year            = 2023 # Specify the year you want to analyze. Has to be one of 2019, 2023
    plot_version    = 'simple' # Specifies which apportionments show up in your plots. 
                               # Needs to be one of 'no quorum', 'simple', 'non-wpba', 'normal'
    plot_dhont      = False # Specifies whether biproportional apportionment with upper
                            # apportionment according to D'Hont is plotted.
    quorum          = [1,5] # Specifies the quorum a party needs to reach in order to be
                            # entitled to seats. The first number in the list represents the
                            # national quorum. Any party that gets at least that many percent
                            # of the votes nationwide can qualify for seats. The second number
                            # in the list is the regional quorum. Any party that gets at least
                            # that many percent of the votes in one region is also qualified
                            # for seats in the national parliament. If you do not want to use
                            # any quorum, you can set `quorum = None`.
    plot_cantons    = False # Indicates which cantonal seat distributions are plotted. You can
                            # use 'all' to plot all cantons, 'BE' (or any other two letter
                            # canton abbreviation) to plot just one canton or a list ['BE',
                            # 'VD', 'ZH'] to plot several cantons.
    save_fig        = 'Plots/' # Indicates whether plots are saved. Use False to not save plots
                               # or a path to an existing directory (ending with '/' or '\\')
                               # to save figures in that directory.
    save_excel      = 'apportionments.xlsx' # Whether to save the results in an Excel file. Has to be
                            # False or a path to an Excel file (either existing one or one to
                            # be created) to which sheets will be appended or replaced.
    
    filename = 'Election_Results\\results_lists.json'
    
    # import votes, party strength, canton names etc.
    if year == 2023:
        votes, bischoff, party_names, canton_names = data_import.get_votes(
            filename, parties=parties, cantons=cantons, fuse=[#['FDP', 'LDP'],
                                                              ['PdA', 'EaG', 'Sol'],
                                                              #['BastA', 'AL'],
                                                              ])
        canton_seats = bischoff.sum(axis=0, dtype=int)
    
    # import 2019 data instead
    elif year == 2019:
        votes = data_import_2019.votes
        bischoff = data_import_2019.current_seats
        party_names = data_import_2019.party_names
        canton_names = data_import_2019.canton_names
        canton_seats = data_import_2019.canton_seats
        party_names = [p.partition('/')[0] for p in party_names]
        for n, p in enumerate(party_names):
            if p in party_rename:
                party_names[n] = party_rename[p]
    
    else:
        raise ValueError('`year` must be one of [2019, 2023].')
    
    if type(save_fig) == str:
        # save_fig = os.path.normpath(save_fig)
        filename = os.path.basename(save_fig)
        folder   = os.path.dirname(save_fig)
        print(folder, filename)
        if filename != '':
            filename = '_' + filename
        filename = str(year) + filename
        save_fig = os.path.normpath(os.path.join(folder, filename))
    
    party_strength = votes/np.sum(votes)*100
    
    
    # Sainte-Laguë
    rounding = np.round
    pw_rounding = protected_winner_rounding(votes, rounding)
    lague = biprop.biproportional_apportionment(votes, rounding, quorum,
                    canton_seats, rounding_method=rounding)
    pwa_lague = biprop.biproportional_apportionment(votes, rounding, quorum,
                    canton_seats, rounding_method=pw_rounding)
    nq_lague = biprop.biproportional_apportionment(votes, rounding, None,
                    canton_seats, rounding_method=pw_rounding)
    simp_lague = biprop.proportional_apportionment(votes, canton_seats,
                    rounding_method=rounding)
    
    # D'hont
    rounding = np.floor
    pw_rounding = protected_winner_rounding(votes, rounding)
    simp_dhont = biprop.proportional_apportionment(votes, canton_seats,
                    rounding_method=rounding)
    if plot_dhont:
        dhont = biprop.biproportional_apportionment(votes, rounding, quorum,
                        canton_seats, rounding_method=rounding)
        pwa_dhont = biprop.biproportional_apportionment(votes, rounding, quorum,
                        canton_seats, rounding_method=pw_rounding)
        nq_dhont = biprop.biproportional_apportionment(votes, rounding, None,
                        canton_seats, rounding_method=pw_rounding)
    
    # define relevant distributions and process them
    distributions = [bischoff]
    dist_names = ['Party strength', 'Hagenbach-Bischoff']
    if plot_version == 'simple':
        distributions.extend([simp_lague, simp_dhont, pwa_lague])
        dist_names.extend(['Simple Sainte-Laguë', 'Simple D\'Hont',
                           'WPBA-Sainte-Laguë'])
        if plot_dhont:
            distributions.extend([pwa_dhont])
            dist_names.extend(['WPBA-D\'Hont'])
    elif plot_version == 'non-wpba':
        distributions.extend([pwa_lague, lague])
        dist_names.extend(['WPBA-Sainte-Laguë', 'BA-Sainte-Laguë'])
        if plot_dhont:
            distributions.extend([pwa_dhont, dhont])
            dist_names.extend(['WPBA-D\'Hont', 'BA-D\'Hont'])
    elif plot_version == 'no quorum':
        distributions.extend([pwa_lague, nq_lague])
        dist_names.extend(['WPBA-Sainte-Laguë', 'No-quorum-Sainte-Laguë'])
        if plot_dhont:
            distributions.extend([pwa_dhont, nq_dhont])
            dist_names.extend(['WPBA-D\'Hont', 'No-quorum-D\'Hont'])
    else:
        distributions.extend([pwa_lague])
        dist_names.extend(['WPBA-Sainte-Laguë'])
        if plot_dhont:
            distributions.extend([pwa_dhont])
            dist_names.extend(['WPBA-D\'Hont'])
    all_party_names = party_names
    distributions, party_strength, party_names = biprop.reorder(
                distributions, party_strength=party_strength,
                party_names=party_names, party_order='size')
    
    # multiply party strength by two such that it matches the number of seats
    party_strength *= 2
    
    if type(save_fig) == str:
        fig_name = save_fig+'_party_strength.png'
    else:
        fig_name = False
    plot_total_result([party_strength, *distributions], party_names,
                      legend=dist_names, save_fig=fig_name)
    
    # reorder parties
    distributions, party_strength, party_names = biprop.reorder(distributions,
                    party_strength=party_strength, party_names=party_names,
                    party_order=party_order)
    dist_names.pop(0)
    
    if type(save_fig) == str:
        fig_name = save_fig+'_parliament.png'
    plot_parliament(distributions, dist_names, party_names,
                    save_fig=fig_name)
    if plot_cantons:
        if type(save_fig) == str:
            fig_name = save_fig+'_detail.png'
        plot_canton(distributions, dist_names, party_names, canton_names,
                    regions=plot_cantons, save_fig=fig_name)
    
    if save_excel:
        print('Appending data to Excel file...')
        if os.path.exists(save_excel):
            mode = 'a'
            if_exists = 'replace'
        else:
            mode = 'w'
            if_exists = None
        with pandas.ExcelWriter(save_excel, mode=mode, if_sheet_exists=if_exists) as writer:
            df = pandas.DataFrame(votes, index=all_party_names, columns=canton_names, dtype=float)
            df.to_excel(writer, sheet_name='Votes')
            df = pandas.DataFrame(party_strength/2, index=party_names, columns=canton_names, dtype=float)
            df.to_excel(writer, sheet_name='Relative party strength')
            for dist, name in zip(distributions, dist_names):
                df = pandas.DataFrame(dist, index=party_names, columns=canton_names, dtype=int)
                df.to_excel(writer, sheet_name=name)
        print('Done!')