def get_mean_speed(speeds):
    speed_map = {}            # get overall mean speed over predefined time interval
    average = 0               # output is single speed value
    mean_speed = 0
    for speed in speeds:
        if len(speed):
            carId = speed[0]
            kmh = speed[1]
            if carId not in speed_map:
                speed_map[carId] = [kmh]
            else:
                val = speed_map[carId]
                val.append(kmh)
    for car,spds in speed_map.items():
        sum_of_speeds = sum(spds)
        if sum_of_speeds > 0:     # for now only considered vehicles coming towards camera
            average = average + (sum_of_speeds/len(spds))
    if len(speed_map) != 0:
        mean_speed = average / len(speed_map)
    return mean_speed

def get_each_mean_speed(speeds):
    speed_map = {}                 # get mean speeds of each of the vehicle present in video
    average_map = {}               # output is dict type
    for speed in speeds:
        if len(speed):
            carId = speed[0]
            kmh = speed[1]
            if carId not in speed_map:
                speed_map[carId] = [kmh]
            else:
                val = speed_map[carId]
                val.append(kmh)
    for car, spds in speed_map.items():
        avg = (sum(spds)/len(spds))
        average_map[car] = avg
    return average_map

if __name__ == "__main__":
    spds = [[1,68],[],[],[2,72],[3,82],[1,70],[2,80],[4,76],[1,72]]
    #spd = [[],[]]
    #print(get_mean_speed(spd))
    print(get_each_mean_speed(spds))
