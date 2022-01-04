# Excel files
import matplotlib.pyplot as plt
import pandas as pd
import csv

# Channels
# 1 Real Time
# 2 OP Speed 1
# 3 OP Torque 1
# 4 OP Speed 2
# 5 OP Torque 2
# 6 IP Speed 1
# 7 IP Torque 1
# 8 Avg Total Output Torque
# 9 Avg Output Delta Torque

data_RealTime = []
data_OPSpeedL = []
data_OPSpeedR = []
data_OPTorqueL = []
data_OPTorqueR = []
data_IPSpeed = []
data_IPTorque = []
data_DeltaOPSpeed = []
data_AvgTotalOPTrq = []
data_DeltaOPTrq = []

column_names = []
sample_rate = 10  # Hz

row_count = 0

path = r"N:\Projects\1306\XT REPORTS\XT-13944 - Loaded Test Rig - EoL Testing\SAMPLE DATA\6JUL2021\full diff test 6_7_21.csv"  # noqa

# # User selected file
# from tkinter import Tk     # from tkinter import Tk for Python 3.x
# from tkinter.filedialog import askopenfilename
#
# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# path = askopenfilename() # show an "Open" dialog box and return the path to the selected file
# print(path)


with open(path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        if row_count < 1:
            column_names.append(row)
        elif row_count > 2:
            data_RealTime.append(row[0])  # 'Real Time'
            data_OPSpeedL.append(float(row[1]))  # 'OP Speed 1'
            data_OPTorqueL.append(float(row[2]))  # 'OP Torque 1'
            data_OPSpeedR.append(float(row[3]))  # 'OP Speed 2'
            data_OPTorqueR.append(float(row[4]))  # 'OP Torque 2'
            data_AvgTotalOPTrq.append(float(row[5]))  # 'Avg Total Output Torque' (Input Torque)
            data_IPSpeed.append(float(row[6]))  # 'IP Speed 1'
            data_IPTorque.append(float(row[7]))  # 'IP Torque 1'
            data_DeltaOPSpeed.append(float(row[8]))  # 'Delta OP Speed'
            data_DeltaOPTrq.append(float(row[9]))  # 'Output Delta Torque' (Locking Torque)
        row_count += 1

print(column_names)


# Convert Real Time to Time
data_Time = []
for i in range(0, len(data_RealTime)):
    x = i * (1 / sample_rate)
    data_Time.append(x)

# Calculate Delta Input Torque (between each data point)
data_IPTorqueDelta = []
for i in range(0, len(data_IPTorque)):
    calc_IPTorqueDelta = data_IPTorque[i] - data_IPTorque[i-5]
    data_IPTorqueDelta.append(calc_IPTorqueDelta)


# Filter data
data_filtered_LockingTrqL = []
data_filtered_LockingTrqR = []
data_filtered_IPTrqL = []
data_filtered_IPTrqR = []
data_filtered_TimeL = []
data_filtered_TimeR = []

k = 0

for i in range(0, len(data_IPTorque)):
    if i < 50:  # Add first 50 points to both L & R data sets
        data_filtered_LockingTrqL.append(data_DeltaOPTrq[i])
        data_filtered_IPTrqL.append(data_AvgTotalOPTrq[i])
        data_filtered_TimeL.append(data_Time[i])
        data_filtered_LockingTrqR.append(abs(data_DeltaOPTrq[i]))
        data_filtered_IPTrqR.append(data_AvgTotalOPTrq[i])
        data_filtered_TimeR.append(data_Time[i])
    elif abs(data_IPTorque[i]) > 20:  # Filter out zero values
        if 5 > data_IPTorqueDelta[i] > -5:  # Attempt to filter out ramp sections
            #  determine if L or R
            if data_DeltaOPTrq[i] > 0:
                data_filtered_LockingTrqL.append(data_DeltaOPTrq[i])
                data_filtered_IPTrqL.append(data_AvgTotalOPTrq[i])
                data_filtered_TimeL.append(data_Time[i])
            else:
                data_filtered_LockingTrqR.append(abs(data_DeltaOPTrq[i]))
                data_filtered_IPTrqR.append(data_AvgTotalOPTrq[i])
                data_filtered_TimeR.append(data_Time[i])


# Group filtered data into single plot points
data_temp_LockingTrqL = []
data_temp_LockingTrqR = []
data_plotting_LockingTrqL = []
data_plotting_LockingTrqR = []
data_temp_IPTrqL = []
data_temp_IPTrqR = []
data_plotting_IPTrqL = []
data_plotting_IPTrqR = []


# Loop through each data point
# if the point is within 1 second of the previous point, it should be grouped
# else, move to the next group
print("[Direction], [IP Trq], [Locking Trq]")
print("------------------------------")
for i in range(0, len(data_filtered_LockingTrqL)):
    time_between_points = data_filtered_TimeL[i] - data_filtered_TimeL[i-1]
    print("TBP:", i, len(data_filtered_LockingTrqL), time_between_points)

    if time_between_points > 1 or i == (len(data_filtered_LockingTrqL) - 1):
        avg_LockingTrqL = round(sum(data_temp_LockingTrqL[sample_rate:]) / len(data_temp_LockingTrqL[sample_rate:]), 3)
        avg_IPTrqL = round(sum(data_temp_IPTrqL[sample_rate:]) / len(data_temp_LockingTrqL[sample_rate:]), 3)

        data_plotting_LockingTrqL.append(avg_LockingTrqL)
        data_plotting_IPTrqL.append(avg_IPTrqL)

        print("[LH], [", avg_IPTrqL, "], [", avg_LockingTrqL, "]")

        data_temp_LockingTrqL = []
        data_temp_IPTrqL = []
    else:
        data_temp_LockingTrqL.append(data_filtered_LockingTrqL[i])
        data_temp_IPTrqL.append(data_filtered_IPTrqL[i])

for i in range(0, len(data_filtered_LockingTrqR)):
    time_between_points = data_filtered_TimeR[i] - data_filtered_TimeR[i - 1]
    print("TBP:", i, len(data_filtered_LockingTrqR), time_between_points)

    if time_between_points > 1 or i == (len(data_filtered_LockingTrqR) - 1):
        avg_LockingTrqR = round(sum(data_temp_LockingTrqR) / len(data_temp_LockingTrqR), 3)
        avg_IPTrqR = round(sum(data_temp_IPTrqR) / len(data_temp_LockingTrqR), 3)

        data_plotting_LockingTrqR.append(avg_LockingTrqR)
        data_plotting_IPTrqR.append(avg_IPTrqR)

        print("[RH], [", avg_IPTrqR, "], [", avg_LockingTrqR, "]")

        data_temp_LockingTrqR = []
        data_temp_IPTrqR = []
    else:
        data_temp_LockingTrqR.append(data_filtered_LockingTrqR[i])
        data_temp_IPTrqR.append(data_filtered_IPTrqR[i])

data_plotting_LH = pd.DataFrame(data_plotting_IPTrqL, columns=['IPTrq'])
data_plotting_LH['LockingTrq'] = data_plotting_LockingTrqL

data_plotting_RH = pd.DataFrame(data_plotting_IPTrqR, columns=['IPTrq'])
data_plotting_RH['LockingTrq'] = data_plotting_LockingTrqR

data_plotting_LH = data_plotting_LH.sort_values('IPTrq')
data_plotting_RH = data_plotting_RH.sort_values('IPTrq')

##############
# FIGURES
##############
fig, ax = plt.subplots(4)

# Plot 1
ax[0].plot(data_Time, data_IPTorque, color='b', label="IPTrq", marker=None)
ax[0].set_xlabel("time")
ax[0].set_ylabel("Torque")
ax[0].set_ylim([-400, 400])
ax[0].set_xlim([0, 350])
ax[0].grid()

# Plot 1, Secondary axis
ax2 = ax[0].twinx()
ax2.plot(data_Time, data_IPTorqueDelta, color='g', label="IPTrqDelta", marker=None)
ax2.set_ylabel("Torque Delta")
ax2.set_ylim([-40, 40])
ax2.grid()

# Plot 2
ax[1].plot(data_Time, data_AvgTotalOPTrq, color='orange', label="IPTrq", marker=None)
ax[1].plot(data_Time, data_DeltaOPTrq, color='purple', label="LockingTrq", marker=None)

ax[1].scatter(data_filtered_TimeL, data_filtered_LockingTrqL, color='magenta', label="IPTrq", marker=".")
ax[1].scatter(data_filtered_TimeR, data_filtered_LockingTrqR, color='magenta', label="LockingTrq", marker=".")

ax[1].scatter(data_filtered_TimeL, data_filtered_IPTrqL, color='lime', marker=".")
ax[1].scatter(data_filtered_TimeR, data_filtered_IPTrqR, color='lime', marker=".")

ax[1].set_xlabel("time")
ax[1].set_ylabel("Torque")
ax[1].set_ylim([-1000, 1000])
ax[1].set_xlim([0, 350])
ax[1].grid()

# Plot 3
ax[2].scatter(data_AvgTotalOPTrq, data_DeltaOPTrq, color='r', label="Diff Locking", marker=".")
ax[2].set_xlabel("Input Torque")
ax[2].set_ylabel("Locking Torque")
ax[2].set_xlim([-1000, 1000])
ax[2].axes.set_xticks(ticks=[-1000, -800, -600, -400, -200, 0, 200, 400, 600, 800, 1000])
ax[2].set_ylim([-1000, 1000])
ax[2].axes.set_yticks(ticks=[-1000, -800, -600, -400, -200, 0, 200, 400, 600, 800, 1000])
ax[2].grid()

# Plot 4
# ---------------------
# filtered data
ax[3].scatter(data_filtered_IPTrqL, data_filtered_LockingTrqL, color='gray', label="Diff Locking L", marker=".")
ax[3].scatter(data_filtered_IPTrqR, data_filtered_LockingTrqR, color='orange', label="Diff Locking R", marker=".")

# grouped data
ax[3].plot(data_plotting_LH['IPTrq'], data_plotting_LH['LockingTrq'], color='black', marker=".")
ax[3].plot(data_plotting_RH['IPTrq'], data_plotting_RH['LockingTrq'], color='red', marker=".")

ax[3].set_xlabel("Input Torque")
ax[3].set_ylabel("Locking Torque")
ax[3].set_xlim([-1000, 1000])
ax[3].axes.set_xticks(ticks=[-1000, -800, -600, -400, -200, 0, 200, 400, 600, 800, 1000])
ax[3].set_ylim([0, 1000])
ax[3].axes.set_yticks(ticks=[0, 200, 400, 600, 800, 1000])
ax[3].grid()

plt.show()
