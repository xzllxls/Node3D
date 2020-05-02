

def AABB_Hit(bbox_min, bbox_max, origin, dir, ray_min=0.001, ray_max=1000000.0):
    if bbox_min[0] >= bbox_max[0] or bbox_min[0] >= bbox_max[0] or bbox_min[0] >= bbox_max[0]:
        return False
    for i in range(3):
        invD = 1.0 / dir[i]
        t0 = (bbox_min[i] - origin[i]) * invD
        t1 = (bbox_max[i] - origin[i]) * invD
        if invD < 0:
            t0, t1 = t1, t0
        ray_min = max(t0, ray_min)
        ray_max = min(t1, ray_max)
        if ray_max <= ray_min:
            return False
    return True

