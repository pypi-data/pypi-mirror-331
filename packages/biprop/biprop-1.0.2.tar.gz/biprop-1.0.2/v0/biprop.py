# -*- coding: utf-8 -*-
"""
biprop.py is python module that can calculate the results of biproportional elections.
Copyright (C) 2024  Talin Herold
"""

import numpy as np
__version__ = '0.1.0'

def get_seats_from_list(list_of_dicts):
    """
    Takes a list where each item corresponds to one region (party). Each item
    should be a dictionary and contain the number of seats of that region (party).
    Returns an array containing the number of seats every region (party) gets.

    Parameters
    ----------
    list_of_dicts : list
        List containing dictionaries. Every item in that list corresponds to one
        region (party) and must contain a dictionary. That dictionary must have
        the number of seats of the corresponding region stored under the key
        'seats'.

    Returns
    -------
    seats : numpy.ndarray of type int
        Numpy array where `seats[i]` are the seats of the i'th region (party) in
        `list_of_dicts`.

    """
    seats = []
    for item in list_of_dicts:
        seats.append(item['seats'])
    return np.array(seats, dtype=int)


def get_seats_from_votes(votes, total_seats, axis=1, rounding_method=np.round,
                         quorum=None, return_divisor=False, max_depth=100,
                         scaling=2):
    """
    Takes an array with the votes and uses a divisor method to assign seats to
    each party (region) according to the total number of votes the party received
    (that were casted in that region). The divisor method that is used is
    determined by the `rounding`-argument. The default divisor method is the
    Sainte-Laguë-method.

    Parameters
    ----------
    votes : array-like, two-dimensional
        2D array where the i'th row corresponds to the votes for the i'th party
        and the j'th column corresponds to the votes casted in the j'th region.
    total_seats : int > 0
        The total number of seats to be assigned. Must be larger than zero.
    axis : 0 or 1, optional
        If `axis == 1`, the seats are apportioned to parties. If `axis == 0`, the
        seats are apportioned to the regions. The default is 1.
    rounding_method : function, optional
        Rounding function that determines the divisor method. The function needs
        to be able to handle both floats and array-like inputs and needs to round
        them to integers. Use `np.round` for the Sainte-Laguë-method and `np.floor`
        for the D'Hont-method. For other methods, see
        'https://en.wikipedia.org/wiki/Highest_averages_method'.
        The default is `numpy.round`.
    quorum : float, (float, float) or NoneType, optional
         ADD DESCRIPTION HERE. The default is None.
    return_divisor : bool, optional
        If True, the final divisor used for the divisor method is returned. The
        default is False.
    max_depth : int, optional
        The maximum number of recursions before a RecursionError is raised. The
        default is 60.
    scaling : float > 1, optional
        This scaling factor determines how fast the algorithm that finds the
        correct seat distribution converges. Smaller values lead to faster
        convergeance. However, too small values can lead to unstable overshoots
        and might result in the algorithem not converging. `scaling` must always be
        larger than one. The default is 2.

    Raises
    ------
    ValueError
        Is raised when `total_seats` is not positive.
    RecursionError
        Is raised when the function did not find the correct seat distribution
        after `max_depth` recursions. If this happens, increasing `max_depth`,
        changing `scaling` or changing to a different divisor method (i.e. changing
        the `rounding_method`-function) may help.

    Returns
    -------
    seats: np.ndarray of type int
        A 1D-array where the i'th entry is the total number of seats of the party
        (region) that corresponds to the i'th row (j'th column) of the
        `votes`-array.
    divisor: float (returned only if `return_divisor` is True)
        The divisor used to calculate the seats from the `votes`-array.

    """
    # check if total_seats is positive
    total_seats = int(total_seats)
    if total_seats < 1:
        raise ValueError(f"`total_seats` has to be a positive integer but is {total_seats}.")
    # modify votes according to quorum
    if type(quorum) != type(None):
        # get quorum-array
        if type(quorum) in (int, float):
            quorum = np.array([quorum, 200], dtype=float)
        else:
            quorum = np.array(quorum, dtype=float)
        # copy votes array
        votes = np.array(votes, dtype=float)
        # if axis==0, transpose votes to be able to perform the same calculations
        if axis == 0:
            votes = votes.T
        NoP, NoR = votes.shape
        # get valid_entry array
        valid = np.zeros((NoP, 1))
        # get total (regional) votes
        tot_votes = votes.sum()
        region_votes = votes.sum(axis=0)
        
        # iterate through every party to find the ones that fulfilled the quorum
        for n, party in enumerate(votes):
            # test if party fulfilled national quorum
            if party.sum()/tot_votes >= quorum[0]/100:
                valid[n,0] = 1
            # otherwise iterate through all regions to test for regional quorum
            else:
                for m, region_res in enumerate(party):
                    if region_res/region_votes[m] >= quorum[1]/100:
                        valid[n,0] = 1
                        break
        
        # multiply the votes of the disqualified parties by 0
        votes *= valid
        # turn votes back to original shape
        if axis == 0:
            votes = votes.T
    
    # get summed votes and provisional apportionment
    votes = np.array(votes, dtype=float).sum(axis=axis)
    divisor = np.sum(votes)/total_seats
    seats = rounding_method(votes/divisor)
    assigned_seats = np.sum(seats, dtype=int)
    
    # if provisional apportionment does not match requirements, start iteration
    if assigned_seats != total_seats:
        factor = 1
        iteration = 0
        too_low = assigned_seats < total_seats
        
        while True:
            if iteration >= max_depth:
                raise RecursionError(f"'get_party_seats' did not converge after {iteration} iterations.")
            iteration += 1
            
            # update votes
            divisor *= 1-(total_seats-assigned_seats)/total_seats * factor
            seats = rounding_method(votes/divisor)
            assigned_seats = np.sum(seats, dtype=int)
            
            if assigned_seats == total_seats:
                break
            elif ((too_low and assigned_seats>total_seats)
                  or (not too_low and assigned_seats<total_seats)):
                too_low = not too_low
                factor /= scaling
    
    if return_divisor:
        return np.array(seats, dtype=int), divisor
    return np.array(seats, dtype=int)

# TODO: Add merge function to merge parties/regions

def reorder(distributions, party_strength=None, delete_irr_parties=True,
            delete_irr_regions=True, party_order=None, party_names=None,
            region_order=None, region_names=None):
    """
    This function takes one or multiple arrays that describe a seat distribution
    and reorders the rows and collumns of the arrays. It can also delete rows and
    columns of parties and regions that did not receive a seat to make the arrays
    more compact.

    Parameters
    ----------
    distributions : list
        A list of one or more distributions. Every distribution needs to be array-
        like with shape `(number_of_parties, number_of_regions)`. The entry in the
        i'th row and j'th column is the number of seats the i'th party received in
        the j'th region. The arrays in `distributions` must only contain integers.
    party_strength : array-like, optional
        An array with shape `(number_of_parties, number_of_regions)` that describes
        the strength of each party in each region, either in total number of votes
        or in percentages. The entry in the i'th row and j'th column must
        correspond to the number (percentage) of votes the i'th party received in
        the j'th region. The default is None.
    delete_irr_parties : bool, optional
        If true, the rows corresponding to parties that did not receive a single
        seat in any of the distributions in `distributions` are deleted. The
        default is True.
    delete_irr_regions : bool, optional
        If true, the columns corresponding to regionss that did not receive a
        single seat in any of the distributions in `distributions` are deleted.
        The default is True.
    party_order : list or 'strength' or 'size' or None, optional
        This describes the desired new order of the party rows. It can either be
        a list of party names, one of the strings'strength' and 'size' or None.
        If `party_order` is None, the order of the parties is not changed.
        If `party_order` is a list, then `party_names` must also be provided. In
        this case `party_order[0]` is the name of the party that should be in the
        first row after reordering, `party_order[1]` the name of the party in the
        second row and so on. `party_order` can contain names that are not in
        `party_names`. These names are skipped and do not get a row. `party_order`
        does not have to include all names in `party_names`. Parties that are
        mentioned in `party_names` but not in `party_order` will show up in the
        reordered arrays after the parties in `party_order` and they will have the
        same relative order as before.
        If `party_order` is 'strength' or 'size', then the parties will be ordered
        according to their strength. If `party_strength` is provided, the strength
        is taken from that array. If it is not provided, the sum of all seats in
        all distributions is used as strength.
        The default is None.
    party_names : list, optional
        A list of length `number_of_parties`. The i'th item of the list must be the
        name of the party that corresponds to the i'th row of the distributions.
        `party_names` must be provided if `party_order` is a list. The default is
        None.
    region_order : list or 'strength' or 'size' or None, optional
        Same as `party_order`, but for regions and columns instead of parties and
        rows. The default is None.
    region_names : list, optional
        Same as `party_names`, but for regions and columns instead of parties and
        rows. The default is None.

    Raises
    ------
    ValueError
        Is raised when an invalid set of parameters is passed.

    Returns
    -------
    new_distributions : list
        A list containing the reordered distributions.
    new_strength : numpy.ndarray (returned only if `party_strength` is not None)
        The reordered `party_strength`.
    new_party_names : list (returned only if `party_names` is not None)
        The new order of the parties. The i'th entry of `new_party_names` is the
        name of the party corresponding to the i'th row of the reordered
        distributions.
    new_region_names : list (returned only if `region_names` is not None)
        The new order of the regions. The j'th entry of `new_region_names` is the
        name of the region corresponding to the j'th column of the reordered
        distributions.

    """
    # convert all distributions to arrays
    distributions = [np.array(dist, dtype=int) for dist in distributions]
    NoP, NoR = distributions[0].shape
    # assert that all distributions have the same shape
    for dist in distributions:
        if dist.shape != (NoP, NoR):
            raise ValueError("All arrays passed in `distributions` must have the same shape.")
    # assert that party_strength has the same shape as the distributions
    if type(party_strength) == np.ndarray or party_strength != None:
        party_strength = np.array(party_strength, dtype=float)
        if party_strength.shape != (NoP, NoR):
            raise ValueError(f"`party_strenght` needs shape {(NoP, NoR)}, but has shape {party_strength.shape}.")
    # assert that party_names has the right shape
    if type(party_names) == np.ndarray:
        party_names = list(party_names)
    if party_names != None and len(party_names) != NoP:
        raise ValueError(f"`party_names` must have length {NoP} but has length {len(party_names)}.")
    # assert that region_names has the right shape
    if type(region_names) == np.ndarray:
        region_names = list(region_names)
    if region_names != None and len(region_names) != NoR:
        raise ValueError(f"`region_names` must have length {NoP} but has length {len(region_names)}.")
    # assert that party_names are provided when party_order is a list
    if party_order != None:
        if type(party_order) == str:
            if party_order.strip().lower() in ('strength', 'size'):
                party_order = 'strength'
            else:
                raise ValueError(f"'{party_order}' is not a valid value for `party_order.`")
        else:
            if party_names == None:
                raise ValueError("When `party_order` is provided and not a string, `party_names` must be provided too.")
    # assert that region_names are provided when region_order is a list
    if region_order != None:
        if type(region_order) == str:
            if region_order.strip().lower() in ('strength', 'size'):
                region_order = 'strength'
            else:
                raise ValueError(f"'{region_order}' is not a valid value for `region_order.`")
        else:
            if region_names == None:
                raise ValueError("When `region_order` is provided and not a string, `region_names` must be provided too.")
    
    if delete_irr_parties:
        relevant_parties = []
        for dist in distributions:
            for n, party in enumerate(dist):
                if n not in relevant_parties and np.sum(party)!=0:
                    relevant_parties.append(n)
        relevant_parties.sort()
        for n, dist in enumerate(distributions):
            distributions[n] = dist[relevant_parties]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[relevant_parties]
        if party_names != None:
            party_names = [party_names[i] for i in relevant_parties]
    
    if delete_irr_regions:
        relevant_regions = []
        for dist in distributions:
            for n, region in enumerate(dist.T):
                if n not in relevant_regions and np.sum(region)!=0:
                    relevant_regions.append(n)
        relevant_regions.sort()
        for n, dist in enumerate(distributions):
            distributions[n] = dist[:, relevant_regions]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[:, relevant_regions]
        if region_names != None:
            region_names = [region_names[i] for i in relevant_regions]
    
    if type(party_order)==str and party_order == 'strength':
        if type(party_strength) == np.ndarray:
            new_order = np.argsort(-party_strength.sum(axis=1))
        else:
            tot_seats = np.array(distributions[0])
            for dist in distributions[1:]:
                tot_seats += dist
            tot_seats = tot_seats.sum(axis=1)
            new_order = np.argsort(-tot_seats)
        for n, dist in enumerate(distributions):
            distributions[n] = dist[new_order]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[new_order]
        if party_names != None:
            party_names = [party_names[i] for i in new_order]
    
    elif party_order != None:
        sort_dict = {party: i for i, party in enumerate(party_order)}
        def value(party):
            if party in sort_dict:
                return sort_dict[party]
            else:
                return len(sort_dict)
        sort_arr = np.array([value(party) for party in party_names])
        new_order = np.argsort(sort_arr)
        for n, dist in enumerate(distributions):
            distributions[n] = dist[new_order]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[new_order]
        party_names = [party_names[i] for i in new_order]
    
    if type(region_order)==str and region_order == 'strength':
        if type(party_strength) == np.ndarray:
            new_order = np.argsort(party_strength.sum(axis=0))
        else:
            tot_seats = np.array(distributions[0])
            for dist in distributions[1:]:
                tot_seats += dist
            tot_seats = tot_seats.sum(axis=0)
            new_order = np.argsort(-tot_seats)
        for n, dist in enumerate(distributions):
            distributions[n] = dist[:, new_order]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[:, new_order]
        if region_names != None:
            region_names = [region_names[i] for i in new_order]
    
    elif region_order != None:
        sort_dict = {region: i for i, region in enumerate(region_order)}
        def value(region):
            if region in sort_dict:
                return sort_dict[region]
            else:
                return len(sort_dict)
        sort_arr = np.array([value(region) for region in region_names])
        new_order = np.argsort(sort_arr)
        for n, dist in enumerate(distributions):
            distributions[n] = dist[:, new_order]
        if type(party_strength) == np.ndarray:
            party_strength = party_strength[:, new_order]
        region_names = [region_names[i] for i in new_order]
    
    match (type(party_strength)==np.ndarray, party_names!=None, region_names!=None):
        case (True, True, True):
            return distributions, party_strength, party_names, region_names
        case (True, True, False):
            return distributions, party_strength, party_names
        case (True, False, True):
            return distributions, party_strength, region_names
        case (True, False, False):
            return distributions, party_strength
        case (False, True, True):
            return distributions, party_names, region_names
        case (False, True, False):
            return distributions, party_names
        case (False, False, True):
            return distributions, region_names
        case _:
            return distributions


def __get_row_divisors__(votes, seats, row_divisors=None, column_divisors=None,
                        rounding_method=np.round, max_depth=100, scaling=2,
                        eps=1e-6):
    """
    Finds and returns row divisors for a votes-array such that the total number
    of seats of the i'th row corresponds to the i'th item of `seats`.
    
    """
    # define row and column vectors
    NoR, NoC = votes.shape
    if type(column_divisors) != np.ndarray and column_divisors == None:
        column_divisors = np.ones((1, NoC), dtype=float)
    if type(row_divisors) != np.ndarray and row_divisors == None:
        row_divisors = np.ones((NoR, 1))
    
    # get provision number of seats
    current_seats = rounding_method(votes/column_divisors/row_divisors)
    current_row_tot = current_seats.sum(axis=1)
    
    # if provisional number of seats does not match requirements, start iteration
    if np.any(current_row_tot != seats):
        factor = np.ones_like(current_row_tot)
        iteration = 0
        too_low = current_row_tot < seats
        
        while True:
            if iteration >= max_depth:
                # print(factor)
                raise RecursionError(f"`get_row_divisors` did not converge after {iteration} iterations.")
            iteration += 1
            
            # get a better guess for row_divisors
            row_divisors *= 1 + ((current_row_tot-seats)/(seats+eps)
                                 * factor).reshape(row_divisors.shape)
            
            # update provisionally assigned seats
            current_seats = rounding_method(votes/column_divisors/row_divisors)
            current_row_tot = current_seats.sum(axis=1)
            
            # if provisional seats match requirements, break
            if np.all(current_row_tot == seats):
                break
            
            # update factor if an over-/undershoot happened
            factor = np.where(((current_row_tot>seats) & too_low)
                              | ((current_row_tot<seats) & (~too_low)),
                              factor/scaling, factor)
            too_low = current_row_tot < seats
    
    return current_seats, row_divisors


def __get_column_divisors__(votes, seats, row_divisors=None, column_divisors=None,
                           rounding_method=np.round, max_depth=100, scaling=2,
                           eps=1e-6):
    """
    Finds and returns row divisors for a votes-array such that the total number
    of seats of the j'th column corresponds to the j'th item of `seats`.
    
    """
    # redefine rounding method such that it can handle votes.T as input
    new_rounding_method = lambda v: rounding_method(v.T).T
    # transpose arrays to transform the column-problem into a row-problem, then
    # call __get_row_divisors__()
    if type(row_divisors) == np.ndarray:
        row_divisors = row_divisors.T
    if type(column_divisors) == np.ndarray:
        column_divisors = column_divisors.T
    current_seats, row_divisors = __get_row_divisors__(
        votes.T, seats, column_divisors, row_divisors, new_rounding_method,
        max_depth, scaling, eps)
    # transpose arrays again to revert them and return them
    return current_seats.T, row_divisors.T


def lower_apportionment(votes, party_seats, region_seats,
                        rounding_method=np.round, return_divisors=False,
                        max_depth=100, scaling=2, eps=1e-6):
    """
    Calculates the lower apportionment. The function returns an array containing
    the number of seats each party gets in each region. This array is chosen such
    that the total number of seats each party gets is equal to the ´party_seats´-
    array and the total number of seats each region gets is equal to the
    ´region_seats´-array.

    Parameters
    ----------
    votes : array-like with shape `(number_of_parties, number_of_regions)`
        2D array where the i'th row corresponds to the votes for the i'th party
        and the j'th column corresponds to the votes casted in the j'th region.
    party_seats: array-like with shape `(number_of_parties,)`
        A 1D-array where the i'th entry is the total number of seats of the party
        that corresponds to the i'th row of the `votes`-array.
    region_seats: array-like with shape `(number_of_regions,)`
        A 1D-array where the j'th entry is the total number of seats of the region
        that corresponds to the j'th column of the `votes`-array.
    rounding_method : function, optional
        Rounding function that determines the divisor method. The function needs
        to be able to handle array-like inputs and needs to round them to integers.
        The argument of `rounding_method` is always an array with the same shape
        like `votes`. This means that one can use this to implement a rounding
        method that never rounds certain parties in certain cantos to zero. This
        is neccessary for a Grisons-like apportionment method where the strongest
        party in each region is guaranteed to win at least one seat in that region.
        Use `np.round` for the Sainte-Laguë-method and `np.floor` for the D'Hont-
        method. For other methods, see
        'https://en.wikipedia.org/wiki/Highest_averages_method'.
        The default is `numpy.round`.
    return_divisors : bool, optional
        Determines whether the party- and region-divisors are returned. The default
        is False.
    max_depth : int, optional
        Maximum number of recursions before a RecursionError is raised. Note that
        in a worst-case scenario, the maximum runtime of this function is
        proportional to `max_depth**2`. The default is 100.
    scaling : float > 1, optional
        This scaling factor determines how fast the algorithm that finds the
        correct seat distribution converges. Smaller values lead to faster
        convergeance. However, too small values can lead to unstable overshoots
        and might result in the algorithem not converging. `scaling` must always be
        larger than one. The default is 2.
    eps : float, optional
        Small value to avoid ZeroDivisionErrors. The default is 1e-6.

    Raises
    ------
    ValueError
        Is raised when the dimensions of the input-arrays do not match up or if
        the number of seats in `party_seats` and `region_seats` do not match.
    RecursionError
        Is raised when the algorithm did not converge after `max_depth` iterations.

    Returns
    -------
    seats: numpy.ndarray of type int
        Array containing the number of seats each party gets in each region. The
        array has the same shape as `votes`. `seats[i,j]` is the number of seats
        that the i'th party gets in the j'th region.
    party_divisors: numpy.ndarray (returned only if `return_divisors` is True)
        The divisors with which each row of `votes` is divided to get the
        `seats`-array. `party_divisors` has shape (number_of_parties, 1).
    region_divisors: numpy.ndarray (returned only if `return_divisors` is True)
        The divisors with which each column of `votes` is divided to get the
        `seats`-array. `region_divisors` has shape (1, number_of_regions).
    
    """
    # convert arguments into numpy arrays
    votes = np.array(votes, dtype=float)
    party_seats = np.array(party_seats, dtype=int)
    region_seats = np.array(region_seats, dtype=int)
    
    # test that arguments have the right shapes
    if len(votes.shape) != 2:
        raise ValueError(f"'votes' has the wrong dimension ({len(votes.shape)} instead of 2).")
    NoP, NoC = votes.shape
    if party_seats.shape != (NoP,):
        raise ValueError(f"'party_seats' has shape {party_seats.shape} but needs shape {(NoP,)}.")
    if region_seats.shape != (NoC,):
        raise ValueError(f"'region_seats' has shape {region_seats.shape} but needs shape {(NoC,)}.")
    if party_seats.sum() != region_seats.sum():
        raise ValueError( "`party_seats` and `region_seats` must have the same total number of seats.")
    
    # get inital estimate for the divisors and seats
    # party_divisors = np.sqrt((votes.sum(axis=1)/(party_seats+eps)).reshape((NoP, 1))/2)
    region_divisors = (votes.sum(axis=0)/(region_seats+eps)).reshape((1, NoC))
    party_divisors = np.ones((NoP, 1))
    # region_divisors = np.ones((1, NoC))
    # get provisional number of seats
    seats = rounding_method(votes/party_divisors/region_divisors)
    
    # calculate assigned party and region seats
    assigned_party_seats = seats.sum(axis=1)
    assigned_region_seats = seats.sum(axis=0)
    
    # if provisional seats do not match the requirements, start iterative process
    if (np.any(assigned_party_seats!=party_seats)
        or np.any(assigned_region_seats!=region_seats)):
        iteration = 0
        while True:
            if iteration >= max_depth: # stop and raise error after max_depth iterations
                raise RecursionError(f"`lower_apportionment` did not converge after {iteration} iterations.")
            iteration += 1
            
            # update region_divisors
            seats, region_divisors = __get_column_divisors__(
                votes, region_seats, party_divisors, region_divisors,
                rounding_method, max_depth, scaling, eps)
            
            # update assigned seats
            assigned_party_seats = seats.sum(axis=1)
            assigned_region_seats = seats.sum(axis=0)
            
            # if seats matches the requirements, break
            if (np.all(assigned_party_seats == party_seats)
                and np.all(assigned_region_seats == region_seats)):
                break
            
            # update party_divisors
            seats, party_divisors = __get_row_divisors__(
                votes, party_seats, party_divisors, region_divisors,
                rounding_method, max_depth, scaling, eps)
            
            # update assigned seats
            assigned_party_seats = seats.sum(axis=1)
            assigned_region_seats = seats.sum(axis=0)
            
            # if seats matches the requirements, break
            if (np.all(assigned_party_seats == party_seats)
                and np.all(assigned_region_seats == region_seats)):
                break
        print(f'Lower apportionment converged after {iteration} iterations.')
    
    # convert seats to integer array
    seats = np.array(seats, dtype=int)
    
    if return_divisors:
        return seats, party_divisors, region_divisors
    return seats


def biproportional_apportionment(votes, party_seats=np.round,
            party_quorum=None, region_seats=np.round, region_quorum=None,
            total_seats=None, rounding_method=np.round, return_upper=False,
            return_divisors=False, max_depth=100, scaling=2, eps=1e-6):
    """
    Uses the biproportional apportionment method and the votes `votes` of an
    election to assign each party and region seats in the parliament.

    Parameters
    ----------
    votes : array-like with shape `(number_of_parties, number_of_regions)`
        2D array where the i'th row corresponds to the votes for the i'th party
        and the j'th column corresponds to the votes casted in the j'th region.
    party_seats: list, numpy.ndarray or function
        A 1D-array where the i'th entry is the total number of seats of the party
        that corresponds to the i'th row of the `votes`-array. Alternatively you
        can pass a function that rounds (arrays of) foats to (arrays) of integers.
        This function will then defines a divisor method that calculates the number
        of seats each party gets from the `votes`-array. The default is np.round.
    party_quorum: float, (float, float) or NoneType, optional
        ADD DESCRIPTION HERE. The default is None.
    region_seats: list, numpy.ndarray or function
        Same as `party_seats`, but for the regions. The default is np.round.
    region_quorum: float, (float, float) or NoneType, optional
        ADD DESCRIPTION HERE. The default is None.
    total_seats: int or NoneType, optional
        The total number of seats in the parliament. Must be provided if neither
        `party_seats` nor `region_seats` is given as list or array, The default
        is None.
    rounding_method : function, optional
        Rounding function that determines the divisor method of the lower
        apportionment. The function needs to be able to handle array-like inputs
        and needs to round them to integers. The argument of `rounding_method` is
        always an array with the same shape like `votes`. This means that one can
        use this to implement a rounding method that never rounds certain parties
        in certain cantos to zero. This is neccessary for a Grisons-like
        apportionment method where the strongest party in each region is guaranteed
        to win at least one seat in that region. Use `np.round` for the Sainte-
        Laguë-method and `np.floor` for the D'Hont-method. For other methods, see
        'https://en.wikipedia.org/wiki/Highest_averages_method'.
        The default is `numpy.round`.
    return_upper : bool, optional
        If True, the function returns two arrays containing the upper apportionment
        of the seats to the parties and regions. The default is False.
    return_divisors : bool, optional
        Determines whether the party- and region-divisors are returned. The default
        is False.
    max_depth : int, optional
        Maximum number of recursions before a RecursionError is raised. Note that
        in a worst-case scenario, the maximum runtime of this function is
        proportional to `max_depth**2`. The default is 100.
    scaling : float > 1, optional
        This scaling factor determines how fast the algorithm that finds the
        correct seat distribution converges. Smaller values lead to faster
        convergeance. However, too small values can lead to unstable overshoots
        and might result in the algorithem not converging. `scaling` must always be
        larger than one. The default is 2.
    eps : float, optional
        Small value to avoid ZeroDivisionErrors. The default is 1e-6.

    Raises
    ------
    ValueError
        Is raised if the shape of the input arrays do not match or if
        `party_seats`, `region_seats` and `total_seats` define a different number
        of total seats.

    Returns
    -------
    seats: numpy.ndarray of type int
        Array containing the number of seats each party gets in each region. The
        array has the same shape as `votes`. `seats[i,j]` is the number of seats
        that the i'th party gets in the j'th region.
    party_seats: numpy.ndarray (returned only if `return_upper` is True)
        1D-array where `party_seats[i]` is the total number of seats the i'th party
        received in the upper apportionment.
    region_seats: numpy.ndarray (returned only if `return_upper` is True)
        1D-array where `party_seats[j]` is the total number of seats the j'th
        region received in the upper apportionment.
    party_divisors: numpy.ndarray (returned only if `return_divisors` is True)
        The divisors with which each row of `votes` is divided to get the
        `seats`-array. `party_divisors` has shape (number_of_parties, 1).
    region_divisors: numpy.ndarray (returned only if `return_divisors` is True)
        The divisors with which each column of `votes` is divided to get the
        `seats`-array. `region_divisors` has shape (1, number_of_regions).

    """
    votes = np.array(votes, dtype=float)
    NoP, NoR = votes.shape
    tot_seats_assigned = total_seats != None
    
    if type(party_seats) in (list, tuple, np.ndarray):
        party_seats = np.array(party_seats, dtype=int)
        tot_party_seats = party_seats.sum()
        if tot_seats_assigned and tot_party_seats!=total_seats:
            raise ValueError(f"Expected a total of {total_seats} in `party_seats` but got {tot_party_seats} seats.")
        elif not tot_seats_assigned:
            tot_seats_assigned = True
            total_seats = tot_party_seats
        if party_seats.shape != (NoP,):
            raise ValueError(f"`party_seats` needs to have shape {(NoP,)} but has shape {party_seats.shape}.")
    
    if type(region_seats) in (list, tuple, np.ndarray):
        region_seats = np.array(region_seats, dtype=int)
        tot_region_seats = region_seats.sum()
        if tot_seats_assigned and tot_region_seats!=total_seats:
            raise ValueError(f"Expected a total of {total_seats} in `region_seats` but got {tot_region_seats} seats.")
        elif not tot_seats_assigned:
            tot_seats_assigned = True
            total_seats = tot_region_seats
        if region_seats.shape != (NoR,):
            raise ValueError(f"`region_seats` needs to have shape {(NoR,)} but has shape {region_seats.shape}.")
    
    if not tot_seats_assigned:
        raise ValueError( "The total number of seats is not defined. It must be provided in either\n"
                         +"`party_seats`, `region_seats` or `tot_seats`.")
    
    if type(party_seats) != np.ndarray:
        party_seats = get_seats_from_votes(votes, total_seats, axis=1,
                        quorum=party_quorum, rounding_method=party_seats,
                        max_depth=max_depth, scaling=scaling)
    
    if type(region_seats) != np.ndarray:
        region_seats = get_seats_from_votes(votes, total_seats, axis=0,
                        quorum=region_quorum, rounding_method=region_seats,
                        max_depth=max_depth, scaling=scaling)
    
    seats, party_divisors, region_divisors = lower_apportionment(
            votes, party_seats, region_seats, rounding_method=rounding_method,
            return_divisors=True, max_depth=max_depth, scaling=scaling, eps=eps)
    
    match (return_upper, return_divisors):
        case (True, True):
            return seats, party_seats, region_seats, party_divisors, region_divisors
        case (True, False):
            return seats, party_seats, region_seats
        case (False, True):
            return seats, party_divisors, region_divisors
        case _:
            return seats
    

def proportional_apportionment(votes, seats, mode='region',
                    rounding_method=np.round, return_divisors=False,
                    max_depth=100, scaling=2, eps=1e-6):
    """
    This function takes the votes of each party in each region and allocates the
    seats in each region seperately to the parties using a divisor method. Since
    the allocations in the diffenrent regions are independent of each other, this
    apportionment method is not a type of biproportional apportionment.

    Parameters
    ----------
    votes : array-like with shape `(number_of_parties, number_of_regions)`
        2D array where the i'th row corresponds to the votes for the i'th party
        and the j'th column corresponds to the votes casted in the j'th region.
    seats : array-like or int
        If `mode=='region'`, `seats` must be an array containing the total number
        of seats of each region and must have shape `(1, number_of_regions)` or
        `(number_of_regions,)`.
        If `mode=='party'`, `seats` must be an array containing the total number
        of seats of each party and must have shape `(number_of_parties, 1)` or
        `(number_of_parties,)`
        If `mode=='total'`, `seats` is the total number of seats and must be a
        positive integer.
    mode : 'region', 'party' or 'total', optional
        Indicates the mode of the apportionment method. If the mode is 'region',
        then the number of seats of each region has to be known and the seats are
        allocated to the parties.
        If the mode is 'party', the number of seats of each party has to be known
        and the seats are allocated to the regions.
        If the mode is 'total', then only the total number of seats has to be known
        and the seats are allocated to both the parties and the regions.
        The default is 'region'.
    rounding_method : function, optional
        Rounding function that determines the divisor method of the lower
        apportionment. The function needs to be able to handle array-like inputs
        and needs to round them to integers. The argument of `rounding_method` is
        always an array with the same shape like `votes`. This means that one can
        use this to implement a rounding method that never rounds certain parties
        in certain cantos to zero. This is neccessary for a Grisons-like
        apportionment method where the strongest party in each region is guaranteed
        to win at least one seat in that region. Use `np.round` for the Sainte-
        Laguë-method and `np.floor` for the D'Hont-method. For other methods, see
        'https://en.wikipedia.org/wiki/Highest_averages_method'.
        The default is `numpy.round`.
    return_divisors : bool, optional
        Determines whether the divisors are returned. The default is False.
    max_depth : int, optional
        Maximum number of recursions before a RecursionError is raised. The default
        is 100.
    scaling : float > 1, optional
        This scaling factor determines how fast the algorithm that finds the
        correct seat distribution converges. Smaller values lead to faster
        convergeance. However, too small values can lead to unstable overshoots
        and might result in the algorithem not converging. `scaling` must always be
        larger than one. The default is 2.
    eps : float, optional
        Small value to avoid ZeroDivisionErrors. The default is 1e-6.

    Raises
    ------
    ValueError
        Is raised when the parameters have wrong shape or invalid values.

    Returns
    -------
    seats: numpy.ndarray of type int
        Array containing the number of seats each party gets in each region. The
        array has the same shape as `votes`. `seats[i,j]` is the number of seats
        that the i'th party gets in the j'th region.
    divisors: numpy.ndarray or float (returned only if `return_divisors` is True)
        The divisors with which `votes` is divided to obtain the `seats`-array.
        If `mode=='region'`, `divisors` is a numpy array with shape
        `(number_of_parties, 1)`.
        If `mode=='party'`, `divisors` is a numpy array with shape
        `(1, number_of_regions)`.
        If `mode=='total'`, `divisors` is a float.

    """
    # get votes array and number of parties and regions
    votes = np.array(votes, dtype=float)
    NoP, NoR = votes.shape
    # assert that mode is valid
    if mode.strip().lower() not in ('region', 'party', 'total'):
        raise ValueError(f"'{mode}' is not a valid value for `mode`.")
    mode = mode.strip().lower()
    # assert that seats has the right format for the given mode
    if mode == 'region':
        seats = np.array(seats, dtype=int).ravel()
        if seats.size != NoR:
            raise ValueError(f"`seats` needs size {NoR} but has size {seats.size}.")
    if mode == 'party':
        seats = np.array(seats, dtype=int).ravel()
        if seats.size != NoP:
            raise ValueError(f"`seats` needs size {NoP} but has size {seats.size}.")
    if mode == 'total':
        try:
            seats = int(seats)
        except (TypeError, ValueError):
            raise ValueError("`seats` must be an integer.")
        if seats < 1:
            raise ValueError(f"`seats` must be positive but is {seats}.")
    
    if mode == 'region':
        # get an inital guess for the column (region) divisors
        divisors = (votes.sum(axis=0)/seats).reshape(1, NoR)
        # call __get_column_divisors__ to get the definite divisors
        assigned_seats, divisors = __get_column_divisors__(votes, seats,
                column_divisors=divisors, rounding_method=rounding_method,
                max_depth=max_depth, scaling=scaling, eps=eps)
    
    elif mode == 'party':
        # get an inital guess for the row (party) divisors
        divisors = (votes.sum(axis=1)/seats).reshape(NoP, 1)
        # call __get_row_divisors__ to get the definite divisors
        assigned_seats, divisors = __get_row_divisors__(votes, seats,
                row_divisors=divisors, rounding_method=rounding_method,
                max_depth=max_depth, scaling=scaling, eps=eps)
    
    else:
        # get provisional divisor and seats
        divisors = votes.sum()/seats
        assigned_seats = rounding_method(votes/divisors)
        total_seats = assigned_seats.sum(dtype=int)
        
        # if assigned seats does not match total seats, start iteration
        if total_seats != seats:
            factor = 1
            iteration = 0
            too_low = total_seats < seats
            
            while True:
                if iteration >= max_depth:
                    raise RecursionError(f"`proportional_apportionment` did not converge after {iteration} iterations.")
                iteration += 1
                
                # update votes
                divisors *= 1 + (total_seats-seats)/seats * factor
                assigned_seats = rounding_method(votes/divisors)
                total_seats = assigned_seats.sum(dtype=int)
                
                if total_seats == seats:
                    break
                elif ((too_low and total_seats>seats)
                      or (not too_low and total_seats<seats)):
                    too_low = not too_low
                    factor /= scaling
    
    # convert assigned_seats into integer array
    assigned_seats = np.array(assigned_seats, dtype=int)
    
    if return_divisors:
        return assigned_seats, divisors
    else:
        return assigned_seats



# if __name__=='__main__':
#     import data_import
#     from data_import import cantons, parties
    
#     rounding_method = np.round
#     total_seats = 200
    
#     votes, og_seats, party_names, canton_names = data_import.get_votes(
#             'Election_Results\\results_lists.json',
#             fuse=[['FDP', 'LDP']],
#             return_seats=True)
#     party_seats = get_seats_from_votes(votes, total_seats,
#                                        rounding_method=rounding_method)
#     # print(party_seats)
#     region_seats = get_seats_from_list(cantons)
    
    
#     seats = lower_apportionment(votes, party_seats, region_seats,
#                                 rounding_method=rounding_method)
    
    
    
#     votes = np.array([[1, 3, 5, 1],
#                       [3, 4, 6, 1],
#                       [2, 4, 4, 0],
#                       [2, 1, 1, 4]], dtype=float)
#     votes += 0.01 * np.random.random((4,4))
#     quorum = (20, 51)
#     total_seats = 10
#     seats = proportional_apportionment(votes, total_seats, mode='total')
    
#     print(seats)
    
    
#     print('\nend')