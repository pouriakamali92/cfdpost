#importing Data
import pandas as pd
import matplotlib.pyplot as plt

files = [
    ('kanal_3_v_1.txt', 'version1'),
    ('kanal_3_v_2.txt', 'Version2'),
    ('kanal_3_v_3.txt', 'Version3'),
    ('kanal_3_v_4.txt', 'Version4'),
]

fig, ax = plt.subplots(figsize=(12, 6))

for filename, label in files:
    data_1 = pd.read_csv(filename, sep=r'\s+', skiprows=4,
                         header=None, skipfooter=1,
                         names=['positions', 'Temperature'],
                         engine='python')
    ax.plot(data_1['positions'], data_1['Temperature'], label=label)

ax.set_xlabel('position (m)')
ax.set_ylabel('Temperature (K)')
ax.set_title('Statische Temperatur entlang der Kanal-3-Wand')
ax.legend()
ax.grid(True)
plt.savefig('kanal3_temperature.png', dpi=150, bbox_inches='tight')
print("Done!")