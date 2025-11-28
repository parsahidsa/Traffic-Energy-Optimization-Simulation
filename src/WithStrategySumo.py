import traci
import sumolib
import random
import time


sumoBinary = sumolib.checkBinary('sumo-gui')


print("Starting simulation...")
traci.start([sumoBinary, "-c", "simpla_config.sumocfg"])


vehicle_speeds = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_positions = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_energy = {f"veh{veh_id}": 0.0 for veh_id in range(10)}
vehicle_departure_times = {f"veh{veh_id}": None for veh_id in range(10)}
vehicle_arrival_times = {f"veh{veh_id}": None for veh_id in range(10)}


vehicle_max_speeds = {f"veh{veh_id}": random.uniform(8, 13.89) for veh_id in range(10)}

start_time = time.time()  


tl_positions = [1455.54]  

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


existing_vehicles = traci.vehicle.getIDList()
for veh_id in existing_vehicles:
    if veh_id.startswith('veh'):
        traci.vehicle.setMaxSpeed(veh_id, vehicle_max_speeds[veh_id])

for step in range(500):  
    current_time = traci.simulation.getTime()
    traci.simulationStep()

    vehicle_ids = traci.vehicle.getIDList()
    for veh_id in vehicle_ids:
        veh_id_str = veh_id
        try:
            speed = traci.vehicle.getSpeed(veh_id_str)
            position = traci.vehicle.getPosition(veh_id_str)[0]
            energy_consumption = traci.vehicle.getElectricityConsumption(veh_id_str)

           
            for tl_pos in tl_positions:
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

        except traci.exceptions.TraCIException as e:
            print(f"Error processing vehicle {veh_id_str}: {e}")
            continue

end_time = time.time()
traci.close()


for veh_id in range(10):
    veh_id_str = f"veh{veh_id}"
    if vehicle_arrival_times[veh_id_str] is not None and vehicle_departure_times[veh_id_str] is not None:
        travel_time = vehicle_arrival_times[veh_id_str] - vehicle_departure_times[veh_id_str]
        print(f"Vehicle {veh_id_str}: Total Travel Time = {travel_time:.3f} s, "
              f"Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")
    else:
        print(f"Vehicle {veh_id_str}: Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")

total_travel_time = end_time - start_time
print(f"Total Travel Time for all vehicles = {total_travel_time:.3f} s")
