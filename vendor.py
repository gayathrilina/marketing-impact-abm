#--------------------------------------------------------------------------
# Overview: This script is used to define the vendor agents
# Author: Gayathri Anil
# Last updated on: 12/17/2022
#--------------------------------------------------------------------------

import math
import numpy as np
import pandas as pd
import random
from mesa import Agent
from scipy.stats import truncnorm

def get_sample(mu=0.5, sigma=0.3, low=0, high=1):
    x = truncnorm((low - mu) / sigma, (high - mu) / sigma, loc=mu, scale=sigma)
    return x.rvs()     

class vendor():

    def __init__(self, prod_variety = 5, health = 4, aesth = 6, price = 3, marketing_intensity = [4, 8, 6, 3]):
        super().__init__()

        self.tick = 0

        self.ticks_per_day = 15
        self.channel_list = ['video_streaming', 'audio_streaming', 'social_media', 'billboard']

        self.product_variety_index = prod_variety
        self.healthy_product_index = health
        self.aesthetic_index = aesth
        self.price_index = price

        self.martketing_intensity = marketing_intensity
        self.marketing_ticks = self.marketing_schedule()
        self.marketing_event_bool = [False, False, False, False]
        self.sales = 0

    def marketing_schedule(self):
        marketing_int = [x/10 for x in self.martketing_intensity]
        marketing_hours = [math.floor(x * self.ticks_per_day) for x in marketing_int]
        marketing_ticks = [[], [], [], []]
        for i in range(len(self.channel_list)):
            ticks = random.sample(range(self.ticks_per_day+1), marketing_hours[i])
            marketing_ticks[i] = ticks

        return marketing_ticks

    def marketing_event(self):
        for i in range(len(self.channel_list)):
            if self.tick in self.marketing_ticks[i]:
                self.marketing_event_bool[i] = True


    def step(self):
        '''
        '''
       


