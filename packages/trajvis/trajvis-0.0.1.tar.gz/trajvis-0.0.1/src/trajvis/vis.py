import numpy as np
import os
import matplotlib.pyplot as plt
import tilemapbase
import tqdm
import math
import imageio.v3 as iio
import argparse

def sample():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--dps", type=int, default=1, help="Data points per second")
    parser.add_argument("--res_factor", type=int, default=1, help="Resolution factor used during interpolation. Set as 1 for no interpolation.")
    args = parser.parse_args()

    save_path = os.path.join(args.save_dir, "traj_high_res.gif")

    # Load agent data
    sample_data = os.path.join(args.dataset_path, "agent_100082.npz")

    data = np.load(sample_data)
    x = data['obs']
    y = data['act']
    z = data['att_mask'] == 1
    np.where(z==1)

    valid_points = x[z]
    lat = valid_points[:, 2]
    lon = valid_points[:, 3]

    create_map_vis(lon, lat, save_path=save_path, dps=args.dps, res_factor=args.res_factor, expand=0.002)


def generate_frame_sequence(x, y, extent, tiles):
    """
    Generate a sequence of frames for a trajectory.
    """
    plotter = tilemapbase.Plotter(extent, tiles, height=600)
    imgs = []
    for idx in tqdm.tqdm(range(1, len(x)+1), desc="Generating frames"):
        sub_x = x[:idx]
        sub_y = y[:idx]

        fig, ax = plt.subplots(layout="tight")
        plotter.plot(ax, tiles, alpha=0.8)
        ax.plot(sub_x, sub_y, color='orange', linewidth=2)
        ax.scatter(sub_x[-1], sub_y[-1], color='black', s=15, zorder=99)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')        
        fig.tight_layout(pad=0, w_pad=0, h_pad=0)
        
        force_canvas_resize(fig, extent)

        image_flat = np.frombuffer(fig.canvas.tostring_argb(), dtype='uint8')
        image = image_flat.reshape(*reversed(fig.canvas.get_width_height()), 4)[:,:,1:4]
        imgs.append(image)
        plt.close(fig)
    return imgs


def make_gif(imgs, filename, dps=10, res_factor=1):
    """
    Create a GIF from a list of images at calculated FPS.
    FPS of GIF = dps*res_factor. Recommended to keep below 50FPS.
    @param imgs: List of images to create GIF from.
    @param filename: Path to save GIF.
    @param dps: Data units per second
    @param res_factor: Resolution factor used during interpolation
    """
    real_fps = dps * res_factor
    iio.imwrite(filename, imgs, fps=real_fps, loop=0)


def force_canvas_resize(fig, extent):
    """
    `Matplotlib` renders images differently when using savefig, copying from the buffer,
    or using show. This function manually resizes the figure to the correct size to remove
    extra padding in the image. Finally, we trigger a redraw.
    """
    fig_w, fig_h = fig.canvas.get_width_height()
    if extent.height > extent.width:
        new_w = math.ceil(extent.width/extent.height * fig_h) / fig.dpi
        fig.set_figwidth(new_w)
    else:
        new_h = math.ceil(extent.height/extent.width * fig_w) / fig.dpi
        fig.set_figheight(new_h)
    fig.canvas.draw()


def high_res_points(x,y,factor=10):
    '''
    Take points listed in two vectors and return them at a higher
    resultion. Create at least factor*len(x) new points that include the
    original points and those spaced in between.

    Returns new x and y arrays as a tuple (x,y).
    '''

    # r is the distance spanned between pairs of points
    r = [0]
    for i in range(1,len(x)):
        dx = x[i]-x[i-1]
        dy = y[i]-y[i-1]
        r.append(np.sqrt(dx*dx+dy*dy))
    r = np.array(r)

    # rtot is a cumulative sum of r, it's used to save time
    rtot = []
    for i in range(len(r)):
        rtot.append(r[0:i].sum())
    rtot.append(r.sum())

    num_points = len(x)
    dr = rtot[-1]/(num_points*factor-1)
    xmod=[x[0]]
    ymod=[y[0]]
    rPos = 0 # current point on walk along data
    rcount = 1 
    while rPos < r.sum():
        x1,x2 = x[rcount-1],x[rcount]
        y1,y2 = y[rcount-1],y[rcount]
        dpos = rPos-rtot[rcount] 
        theta = np.arctan2((x2-x1),(y2-y1))
        rx = np.sin(theta)*dpos+x1
        ry = np.cos(theta)*dpos+y1
        xmod.append(rx)
        ymod.append(ry)
        rPos+=dr
        while rPos > rtot[rcount+1]:
            rPos = rtot[rcount+1]
            rcount+=1
            if rcount>rtot[-1]:
                break

    return xmod,ymod


def create_map_vis(lon, lat, save_path, dps=8, res_factor=5, expand=0.002):
    """
    Create a map visualization of the trajectory in a GIF.
    FPS of GIF = dps*res_factor. Recommended to keep below 50FPS.
    """
    tilemapbase.init(create=True)
    extent = tilemapbase.Extent.from_lonlat(
        lon.min() - expand,
        lon.max() + expand,
        lat.min() - expand,
        lat.max() + expand,
    )

    # Normalize data
    norm_traj = np.array([tilemapbase.project(x, y) for x, y in zip(lon, lat)])
    tiles = tilemapbase.tiles.build_OSM() # Customize options
    x, y = norm_traj[:, 0], norm_traj[:, 1]

    # Optional high res
    if res_factor > 1:
        x, y = high_res_points(x, y, res_factor)

    imgs = generate_frame_sequence(x, y, extent, tiles)

    # Make gif
    make_gif(imgs, save_path, dps=dps, res_factor=res_factor)


if __name__ == "__main__":
    sample()