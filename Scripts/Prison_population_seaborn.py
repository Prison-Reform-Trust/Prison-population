#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:07:15 2019

@author: alex
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.dates as mdates


# Set working directory
os.chdir("/Users/Alex/Prison Reform Trust/Policy and Comms Team - Documents/Python/Weekly prison population")

# Set styles
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale = .8, rc={"grid.linewidth": 0.5})
prt_colours = ["#A4343A", "#A4343A", "#A4343A", "#A4343A"]
font = {'family': 'sans-serif',
        'color':  '#454545',
        }


# Read in datasets 
df = pd.read_csv("prison_population.csv", usecols=['date','population'], parse_dates=['date'])
#set date as index
df.set_index('date',inplace=True)

# Plotting the data
fig, ax = plt.subplots()


ax = sns.lineplot(df.index, df['population'], palette=prt_colours, color="#A4343A",)

# ax = sns.lineplot(data=df,
#             x='date', 
#             y="population",
#             palette=prt_colours,
#             color="#A4343A", )

# sns.despine(left=True, bottom=True)

# Formatting axes and title

#format ticks
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')

ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)



plt.ylabel("People in prison", fontdict=font)
plt.xlabel("", fontdict=font)
plt.yticks(**font)
plt.xticks(**font)


# Add source label of the data
ax.annotate("Source: Ministry of Justice Prison Population Bulletin\n", xy=(16, 1.5),  xycoords='figure pixels', fontsize=7, **font)

# Output the final chart
# plt.savefig(os.path.join('Alex/test.png'), dpi=300, format='png', transparent=True) # use format='svg' or 'pdf' for vector
# fig.autofmt_xdate()
plt.show()


