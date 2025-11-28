import traci
import sumolib
import random
import time

# Check binary
sumoBinary = sumolib.checkBinary('sumo-gui')

# Start the simulation
print("Starting simulation...")
traci.start([sumoBinary, "-c", "simpla_config.sumocfg"])

# Data storage
vehicle_speeds = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_positions = {f"veh{veh_id}": [] for veh_id in range(10)}
vehicle_energy = {f"veh{veh_id}": 0.0 for veh_id in range(10)}
vehicle_departure_times = {f"veh{veh_id}": None for veh_id in range(10)}
vehicle_arrival_times = {f"veh{veh_id}": None for veh_id in range(10)}


vehicle_max_speeds = {f"veh{veh_id}": random.uniform(8, 13.89) for veh_id in range(10)}

start_time = time.time() 

for step in range(500):  # Run the simulation for 500 steps
    current_time = traci.simulation.getTime()
    traci.simulationStep()

    vehicle_ids = traci.vehicle.getIDList()
    for veh_id in vehicle_ids:
        veh_id_str = veh_id
        try:
            speed = traci.vehicle.getSpeed(veh_id_str)
            position = traci.vehicle.getPosition(veh_id_str)[0]
            energy_consumption = traci.vehicle.getElectricityConsumption(veh_id_str)


            max_speed = vehicle_max_speeds[veh_id_str]
            traci.vehicle.setMaxSpeed(veh_id_str, max_speed) 

            if vehicle_departure_times[veh_id_str] is None:
                vehicle_departure_times[veh_id_str] = current_time

            if position >= 5034.152 and vehicle_arrival_times[veh_id_str] is None:
                vehicle_arrival_times[veh_id_str] = current_time

            vehicle_speeds[veh_id_str].append(speed)
            vehicle_positions[veh_id_str].append(position)

            if energy_consumption >= 0:
                vehicle_energy[veh_id_str] += float(energy_consumption)

        except traci.exceptions.TraCIException as e:
            continue

end_time = time.time()
traci.close()

# Print results
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
