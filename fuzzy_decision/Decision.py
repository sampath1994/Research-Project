import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from timeit import default_timer as timer

def init_fuzzy_system():
    # New Antecedent/Consequent objects hold universe variables and membership
    # functions
    vehicle = ctrl.Antecedent(np.arange(0, 35, 1), 'vehicle')
    vSpeed = ctrl.Antecedent(np.arange(0, 60, 1), 'vSpeed')
    pedestrian = ctrl.Antecedent(np.arange(0, 25, 1), 'pedestrian')
    WaitingTime = ctrl.Antecedent(np.arange(0, 60, 1), 'WaitingTime')
    signal = ctrl.Consequent(np.arange(0, 11, 1), 'signal')

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    vehicle['low'] = fuzz.trimf(vehicle.universe, [0, 0, 10])
    vehicle['medium'] = fuzz.trimf(vehicle.universe, [5, 15, 20])
    vehicle['high'] = fuzz.trimf(vehicle.universe, [15, 25, 35])

    WaitingTime['low'] = fuzz.trimf(WaitingTime.universe, [0, 10, 25])
    WaitingTime['medium'] = fuzz.trimf(WaitingTime.universe, [15, 25, 35])
    WaitingTime['high'] = fuzz.trimf(WaitingTime.universe, [20, 40, 60])

    vSpeed['low'] = fuzz.trimf(vSpeed.universe, [5, 15, 30])
    vSpeed['medium'] = fuzz.trimf(vSpeed.universe, [25, 35, 40])
    vSpeed['high'] = fuzz.trimf(vSpeed.universe, [35, 45, 60])

    pedestrian['low'] = fuzz.trimf(pedestrian.universe, [0, 5, 10])
    pedestrian['medium'] = fuzz.trimf(pedestrian.universe, [8, 12, 16])
    pedestrian['high'] = fuzz.trimf(pedestrian.universe, [12, 20, 25])

    signal['off'] = fuzz.trimf(signal.universe, [0, 0, 6])
    signal['on'] = fuzz.trimf(signal.universe, [0, 6, 10])

    # You can see how these look with .view()
    # vehicle.view()
    # plt.show()
    #
    # WaitingTime.view()
    # plt.show()
    #
    # vSpeed.view()
    # plt.show()
    #
    # pedestrian.view()
    # plt.show()
    #
    # signal.view()
    # plt.show()


    rule1 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['low'], signal['off'])
    rule2 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['low'], signal['off'])
    rule3 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['low'], signal['off'])
    rule4 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['low'], signal['on'])
    rule5 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['low'], signal['on'])
    rule6 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['low'], signal['off'])
    rule7 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['low'], signal['on'])
    rule8 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['low'], signal['on'])
    rule9 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['low'], signal['on'])

    rule10 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule11 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule12 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule13 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule14 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule15 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['medium'], signal['off'])
    rule16 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['medium'], signal['on'])
    rule17 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['medium'], signal['on'])
    rule18 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['medium'], signal['off'])

    rule19 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule20 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule21 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule22 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule23 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule24 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule25 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule26 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['high'], signal['off'])
    rule27 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['low'] & vSpeed['high'], signal['off'])

    rule28 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule29 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule30 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['low'], signal['off'])
    rule31 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule32 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule33 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule34 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule35 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['low'], signal['on'])
    rule36 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['low'], signal['on'])

    rule37 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['medium'], signal['on'])
    rule38 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['medium'], signal['off'])
    rule39 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['medium'], signal['off'])
    rule40 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['medium'], signal['on'])
    rule41 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['medium'], signal['off'])
    rule42 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['medium'], signal['off'])
    rule43 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['medium'], signal['on'])
    rule44 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['medium'], signal['on'])
    rule45 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['medium'], signal['off'])

    rule46 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule47 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule48 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule49 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule50 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule51 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule52 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule53 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['high'], signal['off'])
    rule54 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['medium'] & vSpeed['high'], signal['off'])

    rule55 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule56 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule57 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule58 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule59 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule60 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule61 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule62 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['low'], signal['on'])
    rule63 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['low'], signal['on'])

    rule64 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule65 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule66 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['medium'], signal['off'])
    rule67 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule68 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule69 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['medium'], signal['off'])
    rule70 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule71 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['medium'], signal['on'])
    rule72 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['medium'], signal['on'])

    rule73 = ctrl.Rule(vehicle['low'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule74 = ctrl.Rule(vehicle['medium'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule75 = ctrl.Rule(vehicle['high'] & WaitingTime['low'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule76 = ctrl.Rule(vehicle['low'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule77 = ctrl.Rule(vehicle['medium'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule78 = ctrl.Rule(vehicle['high'] & WaitingTime['medium'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule79 = ctrl.Rule(vehicle['low'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['high'], signal['on'])
    rule80 = ctrl.Rule(vehicle['medium'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['high'], signal['off'])
    rule81 = ctrl.Rule(vehicle['high'] & WaitingTime['high'] & pedestrian['high'] & vSpeed['high'], signal['off'])

    # rule1.view()
    # plt.show()


    signal_ctrl = ctrl.ControlSystem([rule1, rule2, rule3,
                                      rule4, rule5, rule6,
                                      rule7, rule8, rule9,

                                      rule10, rule11, rule12,
                                      rule13, rule14, rule15,
                                      rule16, rule17, rule18,

                                      rule19, rule20, rule21,
                                      rule22, rule23, rule24,
                                      rule25, rule26, rule27,

                                      rule28, rule29, rule30,
                                      rule31, rule32, rule33,
                                      rule34, rule35, rule36,

                                      rule37, rule38, rule39,
                                      rule40, rule41, rule42,
                                      rule43, rule44, rule45,

                                      rule46, rule47, rule48,
                                      rule49, rule50, rule51,
                                      rule52, rule53, rule54,

                                      rule55, rule56, rule57,
                                      rule58, rule59, rule60,
                                      rule61, rule62, rule63,

                                      rule64, rule65, rule66,
                                      rule67, rule68, rule69,
                                      rule70, rule71, rule72,

                                      rule73, rule74, rule75,
                                      rule76, rule77, rule78,
                                      rule79, rule80, rule81])

    TLsignal = ctrl.ControlSystemSimulation(signal_ctrl)
    return TLsignal


# return True if pedestrian should get green light.
def get_decision(simulation, vehicle_count, pedestrian_count, avg_vehicle_speed, pedestrian_wait_time, requirnment_thresh):
    vehicle_count_buff = 1
    pedestrian_count_buff = 1
    avg_vehicle_speed_buff = 1
    pedestrian_wait_time_buff = 1
    # Edge case handling
    if vehicle_count == 0 and pedestrian_count > 0:
        return True
    if vehicle_count == 0 and pedestrian_count == 0:  # general rule in streets
        return False
    if pedestrian_count == 0:
        return False

    if avg_vehicle_speed == 0:
        avg_vehicle_speed_buff = 10
    elif avg_vehicle_speed >= 60:
        avg_vehicle_speed_buff = 59
    else:
        avg_vehicle_speed_buff = avg_vehicle_speed

    if pedestrian_wait_time == 0:
        pedestrian_wait_time_buff = 1
    elif pedestrian_wait_time >= 60:
        pedestrian_wait_time_buff = 59
    else:
        pedestrian_wait_time_buff = pedestrian_wait_time

    if vehicle_count >= 35:
        vehicle_count_buff = 34
    else:
        vehicle_count_buff = vehicle_count

    if pedestrian_count >= 25:
        pedestrian_count_buff = 24
    else:
        pedestrian_count_buff = pedestrian_count

    simulation.input['vehicle'] = vehicle_count_buff
    simulation.input['pedestrian'] = pedestrian_count_buff
    simulation.input['vSpeed'] = avg_vehicle_speed_buff
    simulation.input['WaitingTime'] = pedestrian_wait_time_buff

    if pedestrian_wait_time > 5 and pedestrian_wait_time < 40:
        start = timer()
        try:
            simulation.compute()
        except Exception as e:
            print("[Error log]: ", vehicle_count_buff, pedestrian_count_buff, avg_vehicle_speed_buff, pedestrian_wait_time_buff)
            print(repr(e))
        end = timer()
        print(end - start)
        out_val = simulation.output['signal']
        print(out_val)
        if out_val > requirnment_thresh:
            return True  # pedestrian get green light
        else:
            return False  # vehicles get green light
    elif pedestrian_wait_time <= 5:
        print("Pedestrians cannot cross the road, vehicles are moving")
        return False
    elif pedestrian_wait_time > 40:
        print("Now pedestrians can cross the road")
        return True



if __name__ == "__main__":
    sim = init_fuzzy_system()
    #               vehicle_count (35), pedestrian_count (25), avg_vehicle_speed (60), pedestrian_wait_time (60)
    traffic_data = [(30, 5, 25, 5),   # take time as t,  t=5
                    (10, 15, 55, 10),  # t=10
                    (12, 15, 40, 20),  # t=20
                    (12, 20, 45, 25),  # t=25
                    (10, 20, 45, 30),  # t=30
                    (8, 22, 50, 38),
                    (1, 6, 10, 1)]  # t=38

    for i in traffic_data:
        print(get_decision(sim, i[0], i[1], i[2], i[3], 4))  # requirement_threshold taken as 4
        # print True if pedestrians get green light
