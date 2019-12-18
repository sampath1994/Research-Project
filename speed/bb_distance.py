import math
def get_distance(bb1, bb2):
    if isInsideBB(bb1, bb2) or isInsideBB(bb2, bb1):  # both centroids are in each other or one of them in the other
        return 0
    dis1 = calculate(bb1, bb2)
    dis2 = calculate(bb2, bb1)
    if dis1 < dis2:
        return dis1
    else:
        return dis2

def dist(x1, y1, x2, y2):
    dis = (x2-x1)**2 + (y2-y1)**2
    return int(math.sqrt(dis))

def calculate(bb_previous, bb_current): # distance from bb_current centroid to bb_previous is measured
    xp, yp, wp, hp = bb_previous
    xc, yc, wc, hc = bb_current
    x = int(xc + (wc/2))
    y = int(yc + (hc/2))
    x1 = xp + wp
    y1 = yp + hp
    if x < xp and y < yp:
        return dist(xp, yp, x, y)
    if x > x1 and y < yp:
        return dist(x1, yp, x, y)
    if x < xp and y1 < y:
        return dist(xp, y1, x, y)
    if x > x1 and y > y1:
        return dist(x1, y1, x, y)
    if yp <= y <= y1:
        if x < xp:
            return xp - x
        else:
            return x - x1
    if xp <= x <= x1:
        if y < yp:
            return yp - y
        else:
            return y - y1

def isInsideBB(bb_previous, bb_current): # centroid of bb_current is inside bb_previous
    xp, yp, wp, hp = bb_previous
    xc, yc, wc, hc = bb_current
    current_centroid_x = int(xc + (wc/2))
    current_centroid_y = int(yc + (hc/2))
    if (xp <= current_centroid_x <= (xp+wp)) and (yp <= current_centroid_y <= (yp+hp)):
        return True
    return False
