# Simulating Concert Ticket Purchases For Specified Venue Capacities, Layouts, and Group Purchase Dynamics

## What This Is
This project is a SimPy-based Discrete Event Simulation of Concert Ticket Purchases for a variety of Specified Venue Capacities, Layouts, and Customer Group Purchase Dynamics and includes a 7-page Academic Paper, SimPy walkthrough, Python Simulation code via a *.py , and a short README. 

## Abstract
This paper details a simulation model built in Python’s SimPy library to estimate data points
regarding online ticket sales for a concert. We discuss how the simulation works, and compare
SimPy to Arena simulation software. Additionally, we highlight the flexibility of SimPy by coding
in specific nuance to the process of online ticket sales, including accommodating different seating
supplies and pricing tiers, whether or not customers wish to purchase only seats next to each
other or are willing to attend with a stratified group, and cart abandonment rates. The model
can easily be modified to accommodate different-sized venues, seating arrangements, and customer
preferences. Based on the model output, we can recommend the number of days in advance tickets
need to go on sale to reach 95% sellout for a venue. We can also suggest how to tier your seating
supply between three ticket tiers: general admission, regular seating, and premium seating to
maximize sales and decrease the time to sell out.

## Basic Code Guidelines
Required Python Imports

import simpy
import pandas as pd
import numpy as np
import random

The Simulation will run one time as it is currently written. To run multiple times wrap the code below line 8 (there is a comment there) in a for loop. Simulation run times are collected in the list "total_simulation_times."

## The remaining descriptive details can be found in the Academic Paper (the PDF file in this repo)
