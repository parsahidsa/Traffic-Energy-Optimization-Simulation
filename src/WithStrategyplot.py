import traci
import sumolib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG)

sumoBinary = sumolib.checkBinary('sumo')

print("Starting simulation...")
traci.start([sumoBinary, "-c", "simpla_config.sumocfg"])

vehicle_speeds = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_positions = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_energy = {f"veh{veh_id}": 0.0 for veh_id in range(10)}
vehicle_departure_times = {f"veh{veh_id}": None for veh_id in range(10)}
vehicle_arrival_times = {f"veh{veh_id}": None for veh_id in range(10)}


vehicle_max_speeds = {f"veh{veh_id}": random.uniform(8, 13.89) for veh_id in range(10)}

start_time = time.time()  


fig, ax = plt.subplots()
lines = {}
energy_texts = {}

for veh_id in range(10):
    line, = ax.plot([], [], label=f"veh{veh_id}")
    lines[f"veh{veh_id}"] = line
    energy_text = ax.text(0, 0, '', fontsize=8, ha='right')
    energy_texts[f"veh{veh_id}"] = energy_text


tl_positions = [1455.54]
traffic_light_lines = {tl_pos: ax.axvline(x=tl_pos, color='r', linestyle='--') for tl_pos in tl_positions}

def init():
    ax.set_xlim(0, 5034.82)
    ax.set_ylim(0, 30)
    ax.xaxis.set_major_locator(plt.MultipleLocator(500))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(100))
    ax.grid(which='both')
    return list(lines.values()) + list(traffic_light_lines.values()) + list(energy_texts.values())

def get_future_state(tl_id, arrival_time):
    current_phase = traci.trafficlight.getPhase(tl_id)
    next_switch = traci.trafficlight.getNextSwitch(tl_id)
    current_time = traci.simulation.getTime()
    remaining_time = next_switch - current_time

 
    program = traci.trafficlight.getAllProgramLogics(tl_id)[0]
    phases = program.getPhases()
    
    while arrival_time > remaining_time:
        arrival_time -= remaining_time
        current_phase = (current_phase + 1) % len(phases)
        remaining_time = phases[current_phase].duration
    
    return phases[current_phase].state

def adjust_speed_to_ensure_green(veh_id, current_speed, distance_to_tl, current_time):
    tls_id = "J1"
    time_to_arrival = distance_to_tl / current_speed if current_speed > 0 else float('inf')
    future_state = get_future_state(tls_id, time_to_arrival)

 
    if 'G' in future_state or 'y' in future_state:
        return current_speed
    
   
    next_switch = traci.trafficlight.getNextSwitch(tls_id)
    current_phase = traci.trafficlight.getPhase(tls_id)
    phases = traci.trafficlight.getAllProgramLogics(tls_id)[0].getPhases()
    time_to_next_green = next_switch - current_time + sum(phases[(current_phase + i) % len(phases)].duration for i in range(2, len(phases), 2))

    required_speed = distance_to_tl / time_to_next_green
    return min(required_speed, traci.vehicle.getAllowedSpeed(veh_id))  

def update(frame):
    current_time = traci.simulation.getTime()
    logging.debug(f"Frame {frame}: Simulation time {current_time}")
    traci.simulationStep()

  
    if frame > 100:
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


                max_speed = vehicle_max_speeds[veh_id_str]
                traci.vehicle.setMaxSpeed(veh_id_str, max_speed)


                for tl_pos in [1455.54]:
                    distance_to_tl = tl_pos - position
                    if distance_to_tl <= 200:
                        adjusted_speed = adjust_speed_to_ensure_green(veh_id_str, speed, distance_to_tl, current_time)
                        traci.vehicle.setSpeed(veh_id_str, adjusted_speed)

                if vehicle_departure_times[veh_id_str] is None:
                    vehicle_departure_times[veh_id_str] = current_time

                if position >= 5034.152 and vehicle_arrival_times[veh_id_str] is None:
                    vehicle_arrival_times[veh_id_str] = current_time

                vehicle_speeds[veh_id_str].append(speed)
                vehicle_positions[veh_id_str].append(position)

                if energy_consumption >= 0:
                    vehicle_energy[veh_id_str] += float(energy_consumption)


                if len(vehicle_positions[veh_id_str]) > 1:  
                    lines[veh_id_str].set_data(vehicle_positions[veh_id_str], vehicle_speeds[veh_id_str])
                    energy_texts[veh_id_str].set_position((vehicle_positions[veh_id_str][-1], vehicle_speeds[veh_id_str][-1]))
                    energy_texts[veh_id_str].set_text(f"{vehicle_energy[veh_id_str] / 1000:.2f} kJ")

            except traci.exceptions.TraCIException:
                logging.exception(f"Error processing vehicle {veh_id_str}")
                continue

    return list(lines.values()) + list(traffic_light_lines.values()) + list(energy_texts.values())

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
    else:
        print(f"Vehicle {veh_id_str}: Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")

#print(f"Total Travel Time for all vehicles = {total_travel_time:.3f} s")
#print(f"Total Energy Consumption for all vehicles = {total_energy / 1000:.2f} kJ")
