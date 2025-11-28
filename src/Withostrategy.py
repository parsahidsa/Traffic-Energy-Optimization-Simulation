import traci
import sumolib
import time
import random

sumoBinary = sumolib.checkBinary('sumo')

traci.start([sumoBinary, "-c", "simpla_config.sumocfg"])

vehicle_energy = {f"veh{veh_id}": 0.0 for veh_id in range(10)}
vehicle_departure_times = {f"veh{veh_id}": None for veh_id in range(10)}
vehicle_arrival_times = {f"veh{veh_id}": None for veh_id in range(10)}

start_time = time.time()  

def update(frame):
    current_time = traci.simulation.getTime()
    traci.simulationStep()

    for veh_id in range(10):
        veh_id_str = f"veh{veh_id}"
        if veh_id_str in traci.vehicle.getIDList():
            try:
          
                random_speed = random.uniform(11, 12)
                traci.vehicle.setSpeed(veh_id_str, random_speed)
                
                position = traci.vehicle.getPosition(veh_id_str)[0]
                energy_consumption = traci.vehicle.getElectricityConsumption(veh_id_str)

                if vehicle_departure_times[veh_id_str] is None:
                    vehicle_departure_times[veh_id_str] = current_time

                if position >= 10034.1102 and vehicle_arrival_times[veh_id_str] is None:
                    vehicle_arrival_times[veh_id_str] = current_time

                if energy_consumption >= 0:
                    vehicle_energy[veh_id_str] += float(energy_consumption)

            except traci.exceptions.TraCIException:
                continue

for frame in range(500): 
    update(frame)

end_time = time.time()
traci.close()

total_energy = 0
total_travel_time = end_time - start_time
for veh_id in range(10):
    veh_id_str = f"veh{veh_id}"
    total_energy += vehicle_energy[veh_id_str]
    if vehicle_arrival_times[veh_id_str] is not None and vehicle_departure_times[veh_id_str] is not None:
        travel_time = vehicle_arrival_times[veh_id_str] - vehicle_departure_times[veh_id_str]
        print(f"Vehicle {veh_id_str}: Total Travel Time = {travel_time:.3f} s, Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")
    else:
        print(f"Vehicle {veh_id_str}: Total Energy Consumption = {vehicle_energy[veh_id_str] / 1000:.2f} kJ")

print(f"Total Travel Time for all vehicles = {total_travel_time:.3f} s")
print(f"Total Energy Consumption for all vehicles = {total_energy / 1000:.2f} kJ")
