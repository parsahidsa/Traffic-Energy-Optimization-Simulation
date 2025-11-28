# Traffic-Energy-Optimization-Simulation


This project simulates urban traffic and optimizes energy consumption based on traffic control strategies using **SUMO** and **Python**.

## **Simulation Without Strategy (Before)**
In this simulation, vehicles move randomly without any **optimization** or control. No interaction with **traffic lights** or **sensor data** occurs.

### Key Features:
- Random vehicle movement
- No traffic light control
- Baseline energy consumption and travel time calculation

## **Simulation With Strategy (After)**
In this simulation, we apply traffic control strategies to optimize energy consumption and reduce travel time.

### Key Features:
- **Optimized vehicle speeds** using traffic light control
- **Energy consumption reduction** through intelligent strategies
- Dynamic **traffic light control** based on traffic density and vehicle positions

## **Files:**
- `WithStrategySumo.py`: Simulation with energy optimization strategies.
- `WithoutStrategySumo.py`: Simulation without any strategies.
- `WithStrategyplot.py`: Plots for energy consumption and vehicle speeds.

## **How to Run:**
1. Install **SUMO**:
2. Clone this repository.
3. Run the Python scripts:
   - `WithStrategySumo.py`
   - `WithoutStrategySumo.py`
4. The simulation will run, and you can see the energy consumption and travel time for each vehicle.
