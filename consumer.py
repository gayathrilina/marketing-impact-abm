#--------------------------------------------------------------------------
# Overview: This script defines the consumer agent
# Author: Gayathri Anil
# Last updated on: 12/17/2022
#--------------------------------------------------------------------------


import math
import numpy as np
import pandas as pd
import random
from mesa import Agent
from scipy.stats import truncnorm
import pickle

def get_sample(mu=0.5, sigma=0.3, low=0, high=1):
    x = truncnorm((low - mu) / sigma, (high - mu) / sigma, loc=mu, scale=sigma)
    return x.rvs()
    
class consumer():
    '''
    Consumer type agent
    '''

    def __init__(self, unique_id):

        '''
        Creates a new Consumer type agent
        '''
        super().__init__()
        self.ticks_per_day = 15

        self.id = unique_id
        self.tick = 0

        # maybe move this outside the agent definition
        self.activity_list = ['rest', 'work', 'study', 'commute', 'chill', 'others']
        self.channel_list = ['video_streaming', 'audio_streaming', 'social_media', 'billboard', 'w-o-m', 'none']
        
        # importance given to each marketing in terms of how much it can affect their awareness levels
        self.weightage = [0.7, 0.45, 0.75, 0.3, 0.85]

        # agent traits
        self.product_variety_preference = get_sample(mu = 5, sigma = 4, high = 10)
        self.health_consc = get_sample(mu = 5, sigma = 4, high = 10)
        self.aesth_consc = get_sample(mu = 5, sigma = 4, high = 10)
        self.price_consc = get_sample(mu = 5, sigma = 4, high = 10)

        self.openness = get_sample(mu = 0.5, sigma = 0.35)
        self.consc = get_sample(mu = 0.5, sigma = 0.35)
        self.extro = get_sample(mu = 0.5, sigma = 0.35)
        self.agree = get_sample(mu = 0.5, sigma = 0.35)
        self.neuro = get_sample(mu = 0.5, sigma = 0.35)

        # agent state
        self.activity = random.sample(self.activity_list, 1)[0]
        self.marketing_channel = random.sample(self.channel_list, 1)[0]
        self.coffee_for_the_day = False
        self.coffee_now = False
        self.coffee_choice = None
        self.talk = "Na"
        #self.impression_bool = [False, False]
        self.impression_channel = [random.sample(self.channel_list, k=1)[0], random.sample(self.channel_list, k=1)[0]]

        # agent knowledge base
        self.coffee_experience = [[0, 0], [0,0]] #good, bad for each vendor
        self.impressions = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        self.purchase_ct = [0, 0]
        self.affinity_level = [get_sample(mu = 0.3, sigma = 0.1, high = 10), get_sample(mu = 0.3, sigma = 0.1, high = 10)]
        self.marketing_awareness_level = [get_sample(mu = 0.3, sigma = 0.1, high = 10), get_sample(mu = 0.3, sigma = 0.1, high = 10)]
        self.wom_awareness_level = [get_sample(mu = 0.3, sigma = 0.1, high = 10), get_sample(mu = 0.3, sigma = 0.1, high = 10)]

        self.activity_prob = pd.read_csv("./data/activity-probabilities.csv")
        self.channel_prob = pd.read_csv("./data/channel-activity-probabilities.csv")

        # extroversion is in the range of [0, 1]
        # number of connections is dependent on the agent's extroversion
        self.num_connections = self.extro
        self.connections = []


    def choose_activity(self):

        time = self.tick %self.ticks_per_day
        prob_dist = self.activity_prob[str(time)].tolist()
        activity = random.choices(self.activity_list, weights=prob_dist, k=1)[0]

        return activity

    def get_marketing_channel(self):

        activity = self.activity
        prob_dist = self.channel_prob[str(activity)].tolist()

        channel = random.choices(self.channel_list, weights=prob_dist, k=1)[0]

        return channel
    
    def marketing_exposure(self, ad_by_channel):
        '''
        Checks whether an agent is having a marketing exposure when present on a marketing channel
        '''

        agent_channel = self.marketing_channel
        marketing_channels = ['video_streaming', 'audio_streaming', 'social_media', 'billboard']
        index = marketing_channels.index(agent_channel)

        # iterating over the number of vendors present in the environment
        for i in range(len(ad_by_channel)):
            if ad_by_channel[i][index] == 1:
                # add an impression with certain probability
                impression_bool = int(random.choices([0, 1], weights=[0.5, 0.5], k=1)[0]) # probability of impression by channel to be changesd here
                self.impressions[i][index] =  self.impressions[i][index] + impression_bool
                if impression_bool:
                    self.impression_channel[i] = agent_channel
                else:
                    self.impression_channel[i] = "na"
            else:
                self.impression_channel[i] = "na"


    def marketing_awareness_update(self):
        '''
        Computes agent's awareness towards vendors based on ad impressions it has had for each vendor
        '''

        awareness = [0, 0]
        # iterating through vendors
        for vendor in range(2):
            # iterating through channels other than 'w-o-m' (hence "-1")
            for channel in range(len(self.impressions[0])):
                #print(self.impressions[vendor][channel])
                awareness[vendor] = awareness[vendor] + math.exp(self.weightage[channel]*self.impressions[vendor][channel])

        return awareness

    def buy_coffee(self):
        total_ticks = self.ticks_per_day
        if self.coffee_for_the_day == False: #this check is redundant
            hour = self.tick % total_ticks 
            purchase_probability = 1/(total_ticks-hour)
            purchase_decision = random.choices([True, False], weights=(purchase_probability, (1-purchase_probability)), k=1)[0]
            return purchase_decision

    def purchase_motivation(self):
        '''
        Computes the motivation that the agent has towards the buying the 2 vendors' products
        '''
        motivation = [0, 0]
        for vendor in range(2):
            motivation[vendor] = (1/self.openness) * (self.marketing_awareness_level[vendor] + self.wom_awareness_level[vendor]) + (1/self.consc) * self.affinity_level[vendor]

        return motivation

    def affinity_update(self, vendor):
        '''
        Computes the affinity towards vendors based on experiences
        '''

        affinity = max(0, math.exp(0.9*self.coffee_experience[vendor][0]) - math.exp(0.01*self.coffee_experience[vendor][1]))
        return affinity


    def to_talk_or_not_to_talk(self):

        if self.coffee_experience[0] > 2.5 * self.coffee_experience[1]:
            decision_to_talk = random.choices([True, False], weights=[self.neuro, 1-self.neuro], k=1)[0]

        return decision_to_talk

    def talk(self):

        return None

    def wom_awareness_update(self):

        return None


    def step(self):

        '''
        Perceive environment, update knowledge, buy or not, what to buy
        '''

        print ("Tick: ", self.tick)
        self.activity = self.choose_activity(self)

        if self.w_o_m == True:
            self.awareness_level = self.awareness_update(self)
        
        self.marketing_channel = self.get_marketing_channel(self)

        if self.marketing_channel != 'w-o-m':
            ad_by_channel = [[1, 0, 1, 1], [0, 1, 0, 0]] # 1 or 0 for 'video_streaming', 'audio_streaming', 'social_media', 'billboard' channels
            self.marketing_exposure(self, ad_by_channel)

        if self.impression_bool == True:
            self.awareness_level = self.marketing_awareness_update(self)

        # if the agent hasn't bought coffee for the day
        if self.coffee_for_the_day == False:
            self.coffee_now = self.buy_coffee(self)

            if self.coffee_now:
                motivation_scores = self.purchase_motivation(self)
                brand_choice = random.choices([0,1], weights=(motivation_scores), k=1)[0]
                self.coffee_choice = brand_choice
                experience = random.choices(['good', 'bad'], weights=(self.affinity_level[brand_choice], (1-self.affinity_level[brand_choice])), k=1)[0]
                exp_index = ['good', 'bad'].index(experience)
                self.coffee_experience[brand_choice][exp_index] = self.coffee_experience[brand_choice][exp_index] + 1

                self.affinity_level[brand_choice] = self.affinity_update(self, brand_choice)