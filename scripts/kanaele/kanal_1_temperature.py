#importing Data
import pandas as pd
import matplotlib.pyplot as plt
data_1=pd.read_csv('kanal_1_v_1.txt',sep=r'\s+',skiprows=4,header=None,skipfooter=1,names=['positions','Temperature'],engine='python')
files=[
    ('kanal_1_v_1.txt','version1'),
    ('kanal_1_v_2.txt','Version2'),
    ('kanal_1_v_3.txt','Version3'),
    ('kanal_1_v_4.txt','Version4'),
]
for filename,label in files:
    data_1=pd.read_csv(filename,sep=r'\s+',skiprows=4,header=None,skipfooter=1,names=['positions','Temperature'],engine='python')
    plt.plot(data_1['positions'],data_1['Temperature'],label=label)
plt.xlabel('position (m)')
plt.ylabel('Temperature (K)')
ax = plt.gca()
ax.set_title('Statische Temperatur entlang der Kanal-1-Wand')
plt.legend()
plt.grid(True)
plt.show()