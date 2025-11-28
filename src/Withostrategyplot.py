import traci
import sumolib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import logging


logging.basicConfig(level=logging.DEBUG)

sumoBinary = sumolib.checkBinary('sumo')

print("Starting simulation...")
traci.start([sumoBinary, "-c", "simpla_config.sumocfg"])

vehicle_speeds = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_positions = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_energy = {f"veh{veh_id}": 0.0 for veh_id in range(10)}
vehicle_departure_times = {f"veh{veh_id}": None for veh_id in range(10)}
vehicle_arrival_times = {f"veh{veh_id}": None for veh_id in range(10)}

start_time = time.time()  

fig, ax = plt.subplots()
lines = {}
texts = {}


for veh_id in range(10):
    line, = ax.plot([], [], label=f"veh{veh_id}")
    lines[f"veh{veh_id}"] = line
    text = ax.text(0, 0, '', fontsize=8, ha='right')
    texts[f"veh{veh_id}"] = text


tl_positions = [1455.54]
traffic_light_lines = {tl_pos: ax.axvline(x=tl_pos, color='r', linestyle='--') for tl_pos in tl_positions}

def init():
    ax.set_xlim(0, 4034.82)
    ax.set_ylim(0, 30)
    ax.xaxis.set_major_locator(plt.MultipleLocator(500))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(100))
    ax.grid(which='both')
    return list(lines.values()) + list(traffic_light_lines.values()) + list(texts.values())

def update(frame):
    current_time = traci.simulation.getTime()
    logging.debug(f"Frame {frame}: Simulation time {current_time}")
    traci.simulationStep()


    for tl_pos, traffic_light in traffic_light_lines.items():
        state = traci.trafficlight.getRedYellowGreenState("J1")[0] 
        color = 'r'
        if state == 'G':
            color = 'g'
        elif state == 'y':
            color = 'y'
    
        traffic_light.remove()
        traffic_light_lines[tl_pos] = ax.axvline(x=tl_pos, color=color, linestyle='--')

    for veh_id in range(10):
        veh_id_str = f"veh{veh_id}"
        if veh_id_str in traci.vehicle.getIDList():
            try:
                speed = traci.vehicle.getSpeed(veh_id_str)
                position = traci.vehicle.getPosition(veh_id_str)[0]
                energy_consumption = traci.vehicle.getElectricityConsumption(veh_id_str)

                if vehicle_departure_times[veh_id_str] is None:
                    vehicle_departure_times[veh_id_str] = current_time

                if position >= 4034.152 and vehicle_arrival_times[veh_id_str] is None:
                    vehicle_arrival_times[veh_id_str] = current_time

                vehicle_speeds[veh_id_str].append(speed)
                vehicle_positions[veh_id_str].append(position)

                if energy_consumption >= 0:
                    vehicle_energy[veh_id_str] += float(energy_consumption)

        
                if len(vehicle_positions[veh_id_str]) > 1: 
                    lines[veh_id_str].set_data(vehicle_positions[veh_id_str], vehicle_speeds[veh_id_str])
                    texts[veh_id_str].set_position((vehicle_positions[veh_id_str][-1], vehicle_speeds[veh_id_str][-1]))
                    texts[veh_id_str].set_text(f"{vehicle_energy[veh_id_str] / 1000:.2f} kJ")

            except traci.exceptions.TraCIException:
                logging.exception(f"Error processing vehicle {veh_id_str}")
                continue

    return list(lines.values()) + list(traffic_light_lines.values()) + list(texts.values())


ani = animation.FuncAnimation(fig, update, init_func=init, frames=500, blit=True, interval=100)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

end_time = time.time()
traci.close()

total_energy = 0
total_travel_time = end_time - start_time
for veh_id in range(10):
    veh_id_str = f"veh{veh_id}"
    total_energy += vehicle_energy[veh_id_str]
    if vehicle_arrival_times[veh_id_str] is not None and vehicle_departure_times[veh_id_str] is not None:
        travel_time = vehicle_arrival_times[veh_id_str] - vehicle_departure_times[veh_id_str]
        print(f"Vehicle {veh_id_str}: Total Travel Time = {travel_time:.3f} s, "
              f"Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")
    #else:
        #print(f"Vehicle {veh_id_str}: Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")

#print(f"Total Travel Time for all vehicles = {total_travel_time:.3f} s")
#print(f"Total Energy Consumption for all vehicles = {total_energy / 1000:.2f} kJ")
