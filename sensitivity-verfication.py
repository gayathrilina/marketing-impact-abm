#--------------------------------------------------------------------------
# Overview: This script is used to generate the date from runs for verification-sensitivity analyses
# Author: Gayathri Anil
# Last updated on: 12/17/2022
#--------------------------------------------------------------------------

import random
import numpy as np
import pandas as pd

from vendor import vendor
from consumer import consumer

from scipy.spatial import distance
import pickle

#---------------------------------------------------
# User Inputs
#---------------------------------------------------
# number of consumer agents
num_consumers = 500
keep_consumers_same = True

# number of ticks
num_ticks = 100
num_coffee = 0
num_talk = 0
num_brand = [0,0]

# vendor 1
prod_variety_1 = 4
health_1 = 6
aesth_1 = 7
price_1 = 4

# vendor 2
prod_variety_2 = 7
health_2 = 5
aesth_2 = 5
price_2 = 5

charateristics = [[prod_variety_1, health_1, aesth_1, price_1], [prod_variety_2, health_2, aesth_2, price_2]]

#marketing intensities for vendor agent 1; Order of channels [video, audio, social_media, billboard]
marketing_int_1 = [5, 4, 5, 4]

with open('./data/combinations_subset.pkl', 'rb') as f: 
    combinations= pickle.load(f)

data_dump = []
total = len(combinations)
progress = 1


for intensity_combination in combinations:

    #marketing intensities for vendor agent 2; Order of channels [video, audio, social_media, billboard]
    marketing_int_2 = intensity_combination

    purchase_ct = [0, 0]
    
    print(progress, " of ", total, " settings")
    progress = progress + 1

    #---------------------------------------------------
    # Initialising consumer and vendor agents
    #---------------------------------------------------
    if keep_consumers_same:
        with open('./data/consumers.pkl', 'rb') as f: 
            consumers= pickle.load(f)
    else:
        consumers = []
        for con in range(num_consumers):
            consumers.append(consumer(con))
            with open('./data/consumers.pkl', 'wb') as f: 
                pickle.dump(consumers, f)

    vendor1 = vendor(prod_variety = prod_variety_1, health = health_1, aesth = aesth_1, price = price_1, marketing_intensity = marketing_int_1)
    vendor2 = vendor(prod_variety = prod_variety_2, health = health_2, aesth = aesth_2, price = price_2, marketing_intensity = marketing_int_2)
    
    #---------------------------------------------------
    # Start of Simulation
    #---------------------------------------------------

    # Agent Connections
    # form connections for consumers at the start of simulation
    for con in consumers:
        # number of connections based on extroversion, with lower limit set to 1
        con.num_connections = max(int(con.num_connections * num_consumers), 1)
        # connections
        con.connections = random.sample(range(num_consumers), con.num_connections)
        if con.id in con.connections:
            con.connections.remove(con.id)
        #print("id: ", con.id, "connections: ", con.connections)


    # Ticking through time steps
    for tick in range(num_ticks):
        #print("Tick no.: ", tick)

        # Step 1: Determine whether vendor is advertising at current time step
        vendor1.tick = vendor2.tick = tick
        vendor1.marketing_event()
        vendor2.marketing_event()
        #print(vendor1.marketing_event_bool, vendor2.marketing_event_bool)


        # Step 2: Get activity and marketing channel each consumer is likely to be present on 
        # and update impressions and awareness if they see a vendor's ad
        for con in consumers:
            con.tick = tick
            # reset coffee boolean to False at the start of the day
            if tick % con.ticks_per_day == 0:
                con.coffee_for_the_day = False
                con.coffee_now = False

            # forgetting mechanism
            if tick != 0 and tick % 3*con.ticks_per_day == 0:   
                #print("before --------- ", con.impressions)
                con.impressions = [[max(x - 2, 0) for x in con.impressions[0]], [max(x - 2, 0) for x in con.impressions[1]]]
                #print("after --------- ", con.impressions)

            if con.coffee_for_the_day:
                con.coffee_now = False
                con.coffee_choice = None

            con.activity = con.choose_activity()
            con.marketing_channel = con.get_marketing_channel()
            #print("id: ", con.id, "level: ", con.marketing_awareness_level)
            
            # update impressions if vendor ad channel == consumer channel
            if con.marketing_channel in vendor1.channel_list:
                if vendor1.marketing_event_bool[vendor1.channel_list.index(con.marketing_channel)]: 
                    imp_bool = int(random.choices([0, 1], weights=[0.5, 0.5], k=1)[0])
                    con.impressions[0][vendor1.channel_list.index(con.marketing_channel)] = con.impressions[0][vendor1.channel_list.index(con.marketing_channel)] + imp_bool
                    if imp_bool == 1:
                        con.impression_channel[0] = con.marketing_channel
                    else:
                        con.impression_channel[0] = "Na"
            
                if vendor2.marketing_event_bool[vendor2.channel_list.index(con.marketing_channel)]: 
                    imp_bool = int(random.choices([0, 1], weights=[0.5, 0.5], k=1)[0])
                    con.impressions[1][vendor2.channel_list.index(con.marketing_channel)] = con.impressions[1][vendor2.channel_list.index(con.marketing_channel)] + imp_bool
                    if imp_bool == 1:
                        con.impression_channel[1] = con.marketing_channel
                    else:
                        con.impression_channel[1] = "Na"

            
            # update awareness
            awareness = con.marketing_awareness_update()
            if tick == 0:
                [con.marketing_awareness_level[0]+awareness[0], con.marketing_awareness_level[1]+awareness[1]]
            else:
                con.marketing_awareness_level = awareness

            if con.coffee_for_the_day == False:
                con.coffee_now = con.buy_coffee()

                if con.coffee_now:
                    con.coffee_for_the_day = True
        
                    # calculate motivation towards brands
                    motivation_scores = con.purchase_motivation()
                    #print(motivation_scores)
                    brand_choice = random.choices([0,1], weights=(motivation_scores), k=1)[0]

                    #print("Agent ", con.id, "has bought coffee at tick #", con.tick, "and has bought brand #", brand_choice)

                    con.coffee_choice = brand_choice
                    purchase_ct[brand_choice] = purchase_ct[brand_choice] + 1

                    solidarity = distance.euclidean([con.product_variety_preference, con.health_consc, con.aesth_consc, con.price_consc], charateristics[brand_choice])
                    experience = random.choices(['good', 'bad'], weights=(20-solidarity, solidarity), k=1)[0]
                    exp_index = ['good', 'bad'].index(experience)
                    con.coffee_experience[brand_choice][exp_index] = con.coffee_experience[brand_choice][exp_index] + 1

                    # update affinity based on experience
                    con.affinity_level[brand_choice] = con.affinity_update(brand_choice)

                    # talk to connections
                    if experience == 'good':
                        talk = random.choices([1, 0], weights=(20, 80), k=1)[0]
                        if talk:
                            num_talk = num_talk + 1
                            for i in random.sample(con.connections, int(0.4*(len(con.connections)))):
                                consumers[i].impressions[brand_choice][4] = consumers[i].impressions[brand_choice][4] + 1
        
    dats = [str(marketing_int_1), str(marketing_int_2), purchase_ct[0], purchase_ct[1]]
    data_dump.append(dats)
    temp_data_df = pd.DataFrame(data_dump, columns = ['marketing_setting_1', 'marketing_setting_2', 'purchase_ct_1', 'purchase_ct_2'])
    temp_data_df.to_csv('./results/sen_ver_data_'+str(num_consumers)+'agents'+str(num_ticks)+'ticks_subset.csv', index = False)

data_dump_df = pd.DataFrame(data_dump, columns = ['marketing_setting_1', 'marketing_setting_2', 'purchase_ct_1', 'purchase_ct_2'])
data_dump_df.to_csv('./results/sen_ver_data_'+str(num_consumers)+'agents'+str(num_ticks)+'ticks_subset.csv', index = False)


