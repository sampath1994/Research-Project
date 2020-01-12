import cv2

def is_grouped(bb1, bb2):
    x1, y1, w1, h1 = bb1
    x2, y2, w2, h2 = bb2
    if dh(bb1, bb2) < 5 * max(h1, h2):
        if pv(bb1, bb2) > 0.7:
            if hr(bb1, bb2) > 0.75:
                return True
    return False

def dh(bb1, bb2):  # Horizontal distance between BBs
    x1, _, w1, _ = bb1
    x2, _, w2, _ = bb2
    dist = max(x1, x2) - min(x1+w1, x2+w2)
    return dist

def pv(bb1, bb2):  # overlap between vertical projections of bbs
    nume = -1 * dv(bb1, bb2)
    return nume / min(bb1[3], bb2[3])

def dv(bb1, bb2):  # Vertical distance between BBs
    _, y1, _, h1 = bb1
    _, y2, _, h2 = bb2
    return max(y1, y2) - min(y1+h1, y2+h2)

def hr(bb1, bb2):  # height ratio of BBs
    return min(bb1[3], bb2[3]) / max(bb1[3], bb2[3])

def get_group_bb(bb1 , bb2):
    tx1, ty1, w1, h1 = bb1
    tx2, ty2, w2, h2 = bb2
    bx1 = tx1 + w1
    by1 = ty1 + h1
    bx2 = tx2 + w2
    by2 = ty2 + h2
    tlx = 0
    tly = 0
    brx = 0
    bry = 0
    if tx1 < tx2:
        tlx = tx1
    else:
        tlx = tx2
    if ty1 < ty2:
        tly = ty1
    else:
        tly = ty2
    if by2 > by1:
        bry = by2
    else:
        bry = by1
    if bx2 > bx1:
        brx = bx2
    else:
        brx = bx1
    return tlx, tly, brx, bry

def is_vehicle(tlx, tly, brx, bry, contours, bb1_id, bb2_id):
    width = brx - tlx
    height = bry - tly
    ratio = width / height
    headlight_area = cv2.contourArea(contours[bb1_id]) + cv2.contourArea(contours[bb2_id])
    group_bb_area = width * height
    alignment_ratio = headlight_area / group_bb_area
    if ratio >= 2.0:
        if 0.1 <= alignment_ratio <= 0.6:
            return True
    return False
