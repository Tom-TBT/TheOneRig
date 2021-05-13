# AUTOGENERATED! DO NOT EDIT! File to edit: 06_eyetrack.ipynb (unless otherwise specified).

__all__ = ['interpolate_screen_pos', 'interpolate_checker_pos', 'split_eye_events']

# Cell
import numpy as np
import scipy.interpolate as interpolate
from sklearn import cluster

# Cell
def interpolate_screen_pos(screen_pos, xnew, ynew, kind='linear'):
    """
    Interpolate the position of the xnew and ynew pixels from the original screen_pos.
    `interpolate_checker_pos` should be used instead as it's more user friendly.
    params:
        - screen_pos: Screen positions in shape (17, 10, 2) obtained from calibration (from 80x80 pixel checker corners on a 1280x720px screen)
        - xnew: New pixels indexes in x, in interval [0, 16[
        - ynew: New pixels indexes in y, in interval [0, 9[
    return:
        - Screen positions in shape (len(xnew),len(ynew), 2)
    """
    f = interpolate.interp2d(np.arange(17), np.arange(10), screen_pos[:,:,0].T, kind=kind)
    znew_x = f(xnew, ynew)

    f = interpolate.interp2d(np.arange(17), np.arange(10), screen_pos[:,:,1].T, kind=kind)
    znew_y = f(xnew, ynew)

    return np.stack((znew_x, znew_y), axis=-1)

def interpolate_checker_pos(screen_pos, width_box, height_box, kind='linear'):
    """
    Interpolate the centre of the checkerboard pixels from the screen calibrated position.
    params:
        - screen_pos: Screen positions in shape (16, 9, 2) obtained from calibration (from 80x80 pixel checker corners on a 1280x720px screen)
        - width_box: Width in pixel of a box
        - height_box: Height in pixel of a box
    """
    assert 1280%width_box==0, "unpredictable behaviour if 1280 is not a multiple of width_box"
    assert 720%height_box==0, "unpredictable behaviour if 720 is not a multiple of height_box"
    n_x = 1280/width_box
    n_y = 720/height_box
    xnew = np.arange(16/n_x/2, 16+16/n_x/2, 16/n_x)
    ynew = np.arange(9/n_y/2, 9+9/n_y/2, 9/n_y)
    return interpolate_screen_pos(screen_pos, xnew, ynew, kind=kind)

# Cell
def split_eye_events(eye_tracking, eps=2):
    """
    Split the record where the eye moves. Detection done with clustering on X,Y and time of the eye position.

    params:
        - eye_tracking: Eye traking array of the ellipse fit, in shape (t, (x,y,width,height,angle))
        - eps: Distance to detect eye movements. Adjust this parameter if results are not satisfying
    return:
        - move_indexes, blink_indexes, noise_indexes
    """
    x_pos    = np.array(eye_tracking[:,0])

    X        = np.stack((x_pos, np.linspace(0, len(x_pos), len(x_pos))*.5)).T
    clusters = cluster.dbscan(X, eps=eps, min_samples=5, metric='minkowski', p=2)
    move_indexes = np.where(clusters[1][1:] > clusters[1][:-1])[0] + 1

    noise_indexes = np.where(clusters[1] == -1)[0]
    blink_indexes = np.where(x_pos == 0)[0]

    return move_indexes, blink_indexes, noise_indexes