# Some structure of the simulation below is inspired Lazuardi Al-Muzaki. Read his blog post below.
# https://medium.com/@lazuardy.almuzaki/discrete-event-simulation-using-python-simpy-building-basic-model-1bb34b691797

# Code is written by Lyle Sweet and Alex Shropshire.

import simpy
import pandas as pd
import numpy as np
import random

total_simulation_times = []

### wrap all of the below in a for loop to run experiments. Each Run will take 3-5 seconds. simulation times are stored in the list above.

# arrivals of people to the 'ticket counter'
inter_arrival_time = random.expovariate(1 / 5)  # customer arriving in every 5 minutes

processing_time = {
    # amount of time it takes to choose a section and the number of tickets you want to purchase
    "seat_selection_time": np.random.normal(5, 1),
    # amount of time to decide if you will buy or not.
    "purchase_decision_time": np.random.normal(10, 2)
}

# creates placedholder arrays for what is unsold(0) and sold(1)
tiered_ticket_availability = {
    "general_admission": np.zeros(4056),
    "regular_seating": np.zeros((3, 50, 52)),
    "premium_seating": np.zeros((3, 2, 52))
}


# helper function to look for rows of seats
def zero_runs(a):
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges


# looks for seats sitting next to eachother
def find_n_seats(three_d_array, n):
    for section in range(three_d_array.shape[0]):
        for row in range(three_d_array[section].shape[0]):
            potential_runs = zero_runs(three_d_array[section][row])
            qualified_runs = [run for run in potential_runs if run[1] - run[0] >= n]
            if len(qualified_runs) > 0:
                return section, row, qualified_runs[0][0]


def customer_arrival(env, inter_arrival_time):
    global customer
    global stop_criteria
    global end_time
    customer = 0

    while True:
        # checks to see if at leats 95% of all three tiers are booked
        general_condition = (np.sum(tiered_ticket_availability['general_admission'] == 1) / tiered_ticket_availability[
            'general_admission'].size) >= .95
        regular_condition = (np.sum(tiered_ticket_availability['regular_seating'].flatten() == 1) /
                             tiered_ticket_availability['regular_seating'].size) >= .95
        premium_condition = (np.sum(tiered_ticket_availability['premium_seating'].flatten() == 1) /
                             tiered_ticket_availability['premium_seating'].size) >= .95
        if general_condition and regular_condition and premium_condition:
            end_time = env.now
            stop_criteria.succeed()
        else:
            yield env.timeout(inter_arrival_time)
            customer += 1
            customer_type = random.choices(['picky', 'non_picky'], [0.5, 0.5])[0]
            next_process = start_order_process(env, processing_time, customer, customer_type=customer_type)
            env.process(next_process)


def start_order_process(env, processing_time, customer, customer_type):
    with booking_session.request() as order_request:
        yield order_request
        yield env.timeout(processing_time["seat_selection_time"])

        # probablity customer wants to purchase certain type of ticket
        section_desired = random.choices(['general_admission', 'regular_seating', 'premium_seating'], [0.5, 0.3, 0.2])[
            0]
        # section_desired = 'general_admission'
        tickets_desired = random.randint(1, 10)

        order_ga = book_general_admission(env, processing_time, customer, customer_type,
                                          tickets_desired=tickets_desired, section_desired=section_desired)
        order_regular = book_regular_seating(env, processing_time, customer, customer_type,
                                             tickets_desired=tickets_desired, section_desired=section_desired)
        order_premium = book_premium_seating(env, processing_time, customer, customer_type,
                                             tickets_desired=tickets_desired, section_desired=section_desired)

        if section_desired == 'general_admission':
            env.process(order_ga)
        elif section_desired == 'regular_seating':
            env.process(order_regular)
        elif section_desired == 'premium_seating':
            env.process(order_premium)


def book_general_admission(env, processing_time, customer, customer_type, tickets_desired, section_desired):
    global general_admission_tickets_sold
    global general_admission_tickets_oversell
    with ticket_purchase_action.request() as ga_request:
        yield ga_request
        yield env.timeout(processing_time['purchase_decision_time'])

        if customer_type == "picky":
            tickets_available = np.count_nonzero(tiered_ticket_availability[section_desired] == 0)
            if tickets_available >= tickets_desired:
                continue_shopping = random.choices([1, 0], [0.8, 0.2])[0]
                if continue_shopping:
                    zero_indices = np.where(tiered_ticket_availability[section_desired] == 0)[0]
                    first_n_zero_indices = zero_indices[:tickets_desired]
                    tiered_ticket_availability["general_admission"][first_n_zero_indices] = 1
                    general_admission_tickets_sold += tickets_desired
                    # print(f'{section_desired} purchase made: {tickets_desired}')

            else:
                general_admission_tickets_oversell += tickets_desired
                # print(f"no tickets in {section_desired} available for {customer}")

        else:

            tickets_available = np.count_nonzero(tiered_ticket_availability[section_desired] == 0)

            if tickets_available >= tickets_desired:
                zero_indices = np.where(tiered_ticket_availability[section_desired] == 0)[0]
                first_n_zero_indices = zero_indices[:tickets_desired]
                tiered_ticket_availability[section_desired][first_n_zero_indices] = 1
                general_admission_tickets_sold += tickets_desired
                # print(f'purchase made: {tickets_desired}')

            else:
                general_admission_tickets_oversell += tickets_desired

                # print(f"no tickets available for {customer}")


def book_regular_seating(env, processing_time, customer, customer_type, tickets_desired, section_desired):
    global regular_seating_tickets_sold
    global regular_seating_tickets_oversell
    with ticket_purchase_action.request() as regular_seating_request:
        yield regular_seating_request
        yield env.timeout(processing_time['purchase_decision_time'])

        if customer_type == "picky":
            results = find_n_seats(three_d_array=tiered_ticket_availability[section_desired], n=tickets_desired)
            if results != None:
                section, row, available_start = results
                continue_shopping = random.choices([1, 0], [0.8, 0.2])[0]
                if continue_shopping:
                    tiered_ticket_availability[section_desired][section][row][
                    available_start:available_start + tickets_desired] = 1
                    regular_seating_tickets_sold += tickets_desired
                    # print(f'{section_desired} purchase made: {tickets_desired}')
                # else:
                # print('Regular buyer balked.')
            else:
                regular_seating_tickets_oversell += tickets_desired
                # print(f"no tickets available for {customer}")
        else:
            flat_array = tiered_ticket_availability[section_desired].flatten()
            tickets_available = np.count_nonzero(flat_array == 0)
            if tickets_available >= tickets_desired:
                zero_indices = np.where(flat_array == 0)[0]
                first_n_zero_indices = zero_indices[:tickets_desired]
                flat_array[first_n_zero_indices] = 1
                tiered_ticket_availability[section_desired] = flat_array.reshape(
                    tiered_ticket_availability[section_desired].shape)
                regular_seating_tickets_sold += tickets_desired
                # print(f'{section_desired} purchase made: {tickets_desired}')
            else:
                regular_seating_tickets_oversell += tickets_desired

                # print(f"no tickets available for {customer}")


def book_premium_seating(env, processing_time, customer, customer_type, tickets_desired, section_desired):
    global premium_seating_tickets_sold
    global premium_seating_tickets_oversell
    with ticket_purchase_action.request() as premium_seating_request:
        yield premium_seating_request
        yield env.timeout(processing_time['purchase_decision_time'])

        if customer_type == "picky":

            results = find_n_seats(three_d_array=tiered_ticket_availability[section_desired], n=tickets_desired)

            if results != None:
                section, row, available_start = results
                continue_shopping = random.choices([1, 0], [0.8, 0.2])[0]
                if continue_shopping:
                    tiered_ticket_availability[section_desired][section][row][
                    available_start:available_start + tickets_desired] = 1
                    premium_seating_tickets_sold += tickets_desired

                    # print(f'{section_desired} purchase made: {tickets_desired}')
                # else:
                # print('premium buyer walked.')
            else:
                premium_seating_tickets_oversell += tickets_desired

                # print(f"no tickets available for {customer}")
        else:

            flat_array = tiered_ticket_availability[section_desired].flatten()
            tickets_available = np.count_nonzero(flat_array == 0)
            if tickets_available >= tickets_desired:
                zero_indices = np.where(flat_array == 0)[0]
                first_n_zero_indices = zero_indices[:tickets_desired]
                flat_array[first_n_zero_indices] = 1
                tiered_ticket_availability[section_desired] = flat_array.reshape(
                    tiered_ticket_availability[section_desired].shape)
                # print(f'{section_desired} purchase made: {tickets_desired}')
                premium_seating_tickets_sold += tickets_desired

            else:
                premium_seating_tickets_oversell += tickets_desired

            #    print(f"no tickets available for {customer}")


random.seed(42)  # random seed to preserve same random number generated
env = simpy.Environment()
booking_session = simpy.Resource(env, capacity=1000)  # modern web servers can handle many sessions
ticket_purchase_action = simpy.Resource(env, capacity=1)  # b
customer = 0
general_admission_tickets_sold = 0
regular_seating_tickets_sold = 0
premium_seating_tickets_sold = 0
general_admission_tickets_oversell = 0
regular_seating_tickets_oversell = 0
premium_seating_tickets_oversell = 0
env.process(customer_arrival(env, inter_arrival_time))
stop_criteria = env.event()
start_time = env.now
env.run(until=stop_criteria)

# print statements
general_admission_sellthrough = (
            np.sum(tiered_ticket_availability['general_admission'] == 1) / tiered_ticket_availability[
        'general_admission'].size)
regular_seatting_sellthrough = (
            np.sum(tiered_ticket_availability['regular_seating'].flatten() == 1) / tiered_ticket_availability[
        'regular_seating'].size)
premium_seating_sellthrough = (
            np.sum(tiered_ticket_availability['premium_seating'].flatten() == 1) / tiered_ticket_availability[
        'premium_seating'].size)
print(
    f'general admission sellthrough is {general_admission_sellthrough * 100}% with {general_admission_tickets_sold} tickets.')
print(f'{general_admission_tickets_oversell} general admission tickets missed due to being sold out.')
print(
    f'regular seating sellthrough is {regular_seatting_sellthrough * 100}% with {regular_seating_tickets_sold} tickets.')
print(f'{regular_seating_tickets_oversell} regular seated tickets missed due to being sold out.')
print(
    f'premium seatting sellthrough is {premium_seating_sellthrough * 100}% with {premium_seating_tickets_sold} tickets.')
print(f'{premium_seating_tickets_oversell} premium seated tickets missed due to being sold out.')

total_simulation_time = end_time - start_time
total_simulation_times.append(total_simulation_time)

days = total_simulation_time // (24 * 60)
hours = (total_simulation_time % (24 * 60)) // 60
minutes = round(total_simulation_time % 60, 2)
print(f'Total simulation time: {total_simulation_time:.2f} time units')
print(f'Total simulation time: {days} days, {hours} hours, {minutes} minutes')
