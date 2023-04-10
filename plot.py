#--------------------------------------------------------------------------
# Overview: This script is used to generate plots after the simulation has ended
# Author: Gayathri Anil
# Last updated on: 12/17/2022
#--------------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
#import cv2

#result = cv2.imwrite(r'\dogs-v-cats\dog.100.png’, data)
file_ext = '500agents500ticks'
exp_name = 'exp3.1.1'
file_ext = file_ext + exp_name
sim_data = pd.read_csv('./results/data_' + str(file_ext) + '.csv')

x = []
for i in range(max(sim_data['tick'].tolist())+1):
    x.append(i)


#---------------------------------------------------
# Impressions and Awareness across time
#---------------------------------------------------

y = sim_data.groupby(['tick'])['impressions_1'].mean().tolist()
plt.plot(x, y, "-b", label="mean impressions")
y = sim_data.groupby(['tick'])['awareness_1'].mean().tolist()
y = [math.log(d) for d in y]
plt.plot(x, y, "-r", label="log of mean awareness")
plt.legend(loc="upper left")
plt.xlabel("Ticks")  # add X-axis label
plt.title("Vendor 1 - Avg. Impressions & Awareness by Tick")  # add title
plt.savefig('./results/images/impressions_awareness_1_' + str(file_ext) + '.png')
plt.clf()

y = sim_data.groupby(['tick'])['impressions_2'].mean().tolist()
plt.plot(x, y, "-b", label="mean impressions")
y = sim_data.groupby(['tick'])['awareness_2'].mean().tolist()
y = [math.log(d) for d in y]
plt.plot(x, y, "-r", label="log of mean awareness")
plt.legend(loc="upper left")
plt.xlabel("Ticks")  # add X-axis label
plt.title("Vendor 2 - Avg. Impressions & Awareness by Tick")  # add title
plt.savefig('./results/images/impressions_awareness_2_' + str(file_ext) + '.png')
plt.clf()


#---------------------------------------------------
# Consumption across time
#---------------------------------------------------

subset = sim_data[sim_data['coffee_choice'] == 0] 
x = list(set(subset['tick']))
y = subset.groupby(['tick'])['coffee_choice'].count().tolist()
plt.plot(x, y, "-b", label="purchases")
subset = sim_data[sim_data['coffee_choice'] == 1] 
x = list(set(subset['tick']))
y = subset.groupby(['tick'])['coffee_choice'].count().tolist()
plt.plot(x, y, "-r", label="purchases")
plt.xlabel("Ticks")  # add X-axis label
plt.title("Number of Purchases by Tick")  # add title
plt.savefig('./results/images/purchase_' + str(file_ext) + '.png')
plt.clf()

# #---------------------------------------------------
# # W-o-m and Awareness across time
# #---------------------------------------------------

# subset = sim_data[sim_data['talk'] == 0] 
# y = subset.groupby(['tick'])['talk'].count().tolist()
# plt.plot(x, y, "-b", label="talks about v1")
# subset = sim_data[sim_data['talk'] == 1] 
# y = subset.groupby(['tick'])['talk'].count().tolist()
# plt.plot(x, y, "-r", label="talks about v2")
# plt.xlabel("Ticks")  # add X-axis label
# plt.title("Word of Mouth Transfer of Information by Tick")  # add title
# plt.savefig('./results/images/talk_' + str(file_ext) + '.png')
# plt.clf()

#---------------------------------------------------
# Impressions across time
#---------------------------------------------------

y = sim_data.groupby(['tick'])['impressions_1'].mean().tolist()
plt.plot(x, y, "-b", label="mean impressions for vendor 1")
y = sim_data.groupby(['tick'])['impressions_2'].mean().tolist()
plt.plot(x, y, "-r", label="mean impressions for vendor 2")
plt.legend(loc="upper left")
plt.xlabel("Ticks")  # add X-axis label
plt.title("Average Impressions by Tick")  # add title
plt.savefig('./results/images/impressions_' + str(file_ext) + '.png')
plt.clf()




