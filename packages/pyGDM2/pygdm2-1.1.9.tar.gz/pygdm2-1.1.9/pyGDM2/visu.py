# encoding: utf-8
#
#Copyright (C) 2017-2024, P. R. Wiecha
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Collection of 2D visualization tools for pyGDM2

all 2D plotting is done using `matplotlib`

"""
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import copy

from . import tools 

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

import warnings
WARNING_AUTO_PROJECTION_OFF = False

def _automatic_projection_select(X,Y,Z):
    if  len(np.unique(Z))==1:
        projection = 'xy'
    elif  len(np.unique(Y))==1:
        projection = 'xz'
    elif  len(np.unique(X))==1:
        projection = 'yz'
    else:
        global WARNING_AUTO_PROJECTION_OFF 
        if not WARNING_AUTO_PROJECTION_OFF:
            warnings.warn("3D data. Falling back to XY projection...")
        projection = 'xy'   # fallback
        WARNING_AUTO_PROJECTION_OFF = True
    
    return projection


def _automatic_mesh_detect_2D(geo2d, N_try=20, verbose=0):
    lookup_meshtype = {
        6.83:"cube",
        8.20:"hex1",
        6.31:"hex2",
        9.1:"hex3",
        6.00:"hex_onelayer1",
        8.09:"hex_onelayer2",
        }
    
    step2d = tools.get_step_from_geometry(geo2d)
    
    all_distsum = []
    for  i_try in range(N_try):
        idx_center = np.random.randint(len(geo2d))
        all_distsum.append(np.sort(np.linalg.norm(geo2d - geo2d[idx_center], axis=1))[:7].sum() / step2d)
        
    distsum = np.min(all_distsum)
    try:
        meshtype = lookup_meshtype[np.round(distsum, 2)]
        if verbose:
            print("2dstep= {:.1f}, distsum={:.2f} --> mesh: '{}'".format(step2d, distsum, meshtype))
    except KeyError:
        warnings.warn("Mesh not detected, falling back to 'cubic'.")
        meshtype = 'cube'
    
    return meshtype
        
        
def _get_axis_existing_or_new():
    import matplotlib.pyplot as plt

    if len(plt.get_fignums()) == 0:
        show = True
        ax = plt.subplot()
    else:
        show = False
        ax = plt.gca()
    return ax, show




########################################################################
##                      VISUALIZATION FUNCTIONS
########################################################################
def structure(struct, projection='auto', color='auto', scale=1, 
              borders=3, marker='s', lw=0.1, EACHN=1, tit='',
              colors_multimat=None,
              plot_legend=True, ax=None, absscale=False, 
              set_ax_aspect=True,
              **kwargs):
    """plot structure in 2d, projected to e.g. the XY plane
    
    plot the structure `struct` as a scatter projection to a carthesian plane.
    Either from list of coordinates, or using a simulation definition as input.
    
    kwargs are passed to matplotlib's `scatter`
    
    Parameters
    ----------
    struct : list or :class:`.core.simulation`
          either list of 3d coordinate tuples or simulation description object
          
    projection : str, default: 'auto'
        which 2D projection to plot: "auto", "XY", "YZ", "XZ"
          
    color : str or matplotlib color, default: "auto"
            Color of scatterplot. Either "auto", or matplotlib-compatible color.
            "auto": automatic color selection (multi-color for multiple materials). 
      
    scale : float, default: 1
          symbol scaling in units of half the stepsize
      
    borders : float, default: 3
          additional space limits around plot in units of stepsize
         
    marker : str, default "s" (=squares)
          scatter symbols for plotting meshpoints. Convention of
          matplotlib's `scatter`
    
    lw : float, default 0.1
          line width around scatter symbols. Convention of matplotlib's `scatter`
          
    EACHN : int, default: 1 (=all)
          show each `EACHN` points only
    
    tit : str, default: ""
        title for plot (optional)
    
    colors_multimat : list, default: None
        optional list of colors (matplotlib compatible) to use for different materials
    
    plot_legend : bool, default: True
        whether to add a legend if multi-material structure (requires auto-color enabled)
    
    ax : matplotlib `axes`, default: None (=create new)
           axes object (matplotlib) to plot into
           
    absscale : bool, default: False
          absolute or relative scaling. If True, override internal 
          scaling calculation 
    
    set_ax_aspect : bool, default: True
        set canvas aspect ratio to equal
    
    Returns
    -------
    result returned by matplotlib's `scatter`
    
    """
    from pyGDM2 import structures
    
    # prep
    ax, show = _get_axis_existing_or_new()
    if "show" in kwargs:
        show = kwargs.pop("show")
    if set_ax_aspect:
        ax.set_aspect("equal")
    
    X,Y,Z = tools.get_geometry(struct)
    step = tools.get_step_from_geometry(struct)
    
    if projection.lower() == 'auto':
        projection = _automatic_projection_select(X,Y,Z)
    
    if projection.lower() == 'xy':
        X=X; Y=Y
    elif projection.lower() == 'yz':
        X=Y; Y=Z
    elif projection.lower() == 'xz':
        X=X; Y=Z
    else:
        raise ValueError("Invalid projection parameter!")
    
    ## -- colors for subsets with different materials
    if color == 'auto':
        if hasattr(struct, "struct") or type(struct) == structures.struct:
            if hasattr(struct, "struct"):
                struct = struct.struct
        
            if hasattr(struct.material, '__iter__'):
                materials = [s.__name__ for s in struct.material]
                if len(set(materials)) > 1:
                    a = np.ascontiguousarray(np.transpose([X,Y]))
                    materials_idx = np.unique(a.view([('', a.dtype)]*a.shape[1]), return_index=1)[1]
                    material = np.array(materials)[materials_idx]
                    different_materials = np.unique(materials)
                    indices_subsets = []
                    for struct_fraction in different_materials:
                        indices_subsets.append(np.arange(len(material))[material==struct_fraction])
                else:
                    color = '.2'
            else:
                color = '.2'
        else:
            color = '.2'
    
    ## -- del all duplicates with same x/y coordinates (for plot efficiency)
    X,Y = tools.unique_rows(np.transpose([X,Y]))[::EACHN].T
    
    if not ax:
        ax = plt.gca()
        
    if show:
        plt.gca().set_aspect('equal')
        plt.xlim(X.min()-borders*step, X.max()+borders*step)
        plt.ylim(Y.min()-borders*step, Y.max()+borders*step)
        
    ## -- set scaling depending on structure size
    if not absscale:
        bbox = plt.gca().get_window_extent().transformed(plt.gcf().dpi_scale_trans.inverted())
        axes_pixels_w = bbox.width * plt.gcf().dpi
        axes_pixels_h = bbox.height * plt.gcf().dpi
        maxdist_w = max(X) - min(X) + step
        maxdist_h = max(Y) - min(Y) + step
        N_dp_max_w = maxdist_w / step
        N_dp_max_h = maxdist_h / step
        
        scale_w = scale/2.2 * axes_pixels_w * maxdist_w/((maxdist_w + 2*step*borders) * N_dp_max_w)
        scale_h = scale/2.2 * axes_pixels_h * maxdist_h/((maxdist_h + 2*step*borders) * N_dp_max_h)
        
        scale = min([scale_w, scale_h])
    
    ## --- if multi-material: set maker colors
    if color != 'auto':
        im = ax.scatter(X,Y, marker=marker, s=scale**2,
                        c=color, edgecolors=color, lw=lw, **kwargs)
    else:
        if colors_multimat is None:
            colors = ['C{}'.format(i) for i in range(1,10)]*int(2 + len(indices_subsets)/9.)
        else:
            colors = colors_multimat
        for i, idx in enumerate(indices_subsets):
            col = colors[i]
            if plot_legend:
                label = different_materials[i]
            else:
                label = ''
            im = ax.scatter(X[idx],Y[idx], marker=marker, s=scale**2,
                            c=col, edgecolors=col, label=label, lw=lw, **kwargs)
        if plot_legend:
            plt.legend()
    
    if tit:
        plt.title(tit)
    
    if show:
        plt.xlabel("{} (nm)".format(projection[0]))
        plt.ylabel("{} (nm)".format(projection[1]))
        plt.show()
    
    return im




def _enlarge_struct_geometry(geometry, enlargement, axis1=0, axis2=1, version='colinear'):
    """ Create fake dipoles shifted by enlargement 
    
    Shift in the +/- axis1 direction and +/- axis2 direction. 
    Version 'colinear' is a colinear shift (along axis), 
    Version 'diagonal' is diagonal shift. Subroutine for structure_contour_smooth
    """
    add_geo1 = np.copy(geometry)
    add_geo2 = np.copy(geometry)
    add_geo3 = np.copy(geometry)
    add_geo4 = np.copy(geometry)
    if version == 'colinear' :
        add_geo1[:,axis1] += enlargement
        add_geo2[:,axis1] -= enlargement
        add_geo3[:,axis2] += enlargement
        add_geo4[:,axis2] -= enlargement
    if version == 'diagonal' :
        add_geo1[:,axis1] += enlargement
        add_geo2[:,axis1] += enlargement
        add_geo3[:,axis1] -= enlargement
        add_geo4[:,axis1] -= enlargement
        add_geo1[:,axis2] += enlargement
        add_geo2[:,axis2] -= enlargement
        add_geo3[:,axis2] += enlargement
        add_geo4[:,axis2] -= enlargement

    enlarged_geo = np.concatenate((geometry,add_geo1,add_geo2,add_geo3,add_geo4),axis=0)
    return enlarged_geo

def _alpha_shape(points, alpha, only_outer=True):
    """
    Compute the alpha shape (concave hull) of a set of points.
    :param points: np.array of shape (n,2) points.
    :param alpha: alpha value.
    :param only_outer: boolean value to specify if we keep only the outer border
    or also inner edges.
    :return: set of (i,j) pairs representing edges of the alpha-shape. (i,j) are
    the indices in the points array.
    from : https://karobben.github.io/2022/03/07/Python/point_outline/
    """
    from scipy.spatial import Delaunay
    assert points.shape[0] > 3, "Need at least four points"
    def add_edge(edges, i, j):
        """
        Add an edge between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            assert (j, i) in edges, "Can't go twice over same directed edge right?"
            if only_outer:
                # if both neighboring triangles are in shape, it's not a boundary edge
                edges.remove((j, i))
            return
        edges.add((i, j))
    tri = Delaunay(points)
    edges = set()
    # Loop over triangles:
    # ia, ib, ic = indices of corner points of the triangle
    for ia, ib, ic in tri.simplices:
        pa = points[ia]
        pb = points[ib]
        pc = points[ic]
        # Computing radius of triangle circumcircle
        # www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle
        a = np.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b = np.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c = np.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s = (a + b + c) / 2.0
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        circum_r = a * b * c / (4.0 * area)
        if circum_r < alpha:
            add_edge(edges, ia, ib)
            add_edge(edges, ib, ic)
            add_edge(edges, ic, ia)
    return edges

def _optimize_alpha_value(
    pos2d_exp, alpha_step_limit=1e-3, alpha_init=0.0, time_limit=5.0
):
    """find best alpha_value that still returns an alphashape"""
    import logging
    import time
    import alphashape

    alpha_value = alpha_init
    step = 0.1
    t0 = time.time()

    # solver loop
    original_log_level = logging.getLogger().getEffectiveLevel()
    logging.disable(logging.WARN) # disable alphashape warnings
    while 1:
        _ga = alphashape.alphashape(pos2d_exp, alpha_value + step)
        print(alpha_value + step,_ga.geom_type)
        if _ga.geom_type not in ["Polygon", "MultiPolygon"]:
            step /= 2  # no solution: reduce search step
            if step < alpha_step_limit:
                break # step limit reached
            if time.time() - t0 > time_limit:
                break # time limit reached
        else:
            # solution found, update step
            alpha_value += step

    print(alpha_value,_ga.geom_type)
    logging.disable(original_log_level)
    return alpha_value

def _structure_contour_old(struct, r_contour=1, projection='auto', color='k',
                             borders=3, lw=1, tit='', ax=None, show=True, 
                             split=False, split_axis='x', split_value=0, 
                             phys_accurate=False, phys_enlarge_vers='colinear',
                             **kwargs):
    """Contour around structure via alpha shape
    
    Contour is smoothed by drawing outer line of 2D projection.
    All further kwargs are passed to matplotlib's `ax.plot`.
    
    Contributed by Simon Garrigou.
    
    Parameters
    ----------
    struct : list or :class:`.core.simulation` 
        either list of 3d coordinate tuples or simulation description object
    
    projection : str, default: 'auto'
        which 2D projection to plot: "auto", "XY", "YZ", "XZ"
    
    r_contour : float, default=1
        radius for contour computation : higher = smoother but can go over gaps sometimes

    color : str or matplotlib color, default: "b"
        matplotlib-compatible color for scatter

    borders : float, default: 3
        additional space limits around plot in units of stepsize
    
    lw : float, default: 1
        linewidth as used by `pyplot.plot` (style='lines' only)
        
    tit : str, default: ""
        title for plot (optional)
    
    ax : matplotlib `axes`, default: None (=create new)
        axes object (matplotlib) to plot into
    
    show : bool, default: True
        directly show plot

    split : bool, default : False 
        choice to split the structure in two sub-structures along an axis, 
        contour for each structure is plotted then
        
    split_axis : str, default: 'x'
        axis for the structure split (among 'x', 'y', 'z')
        
    split_value : float, default : 0
        Position on the axis of the splitting plane

    phys_accurate : bool, default : False
        Enlarge structure to take in account the physical meaning of 
        the discretization cell, Working only for cubic for now.
        
    phys_enlarge_vers : str, default : 'colinear'
        'colinear' or 'diagonal' for the artificial enlargement 
        procedure, will play at the corners    
    """
    geo = tools.get_geometry(struct)
    step = tools.get_step_from_geometry(struct)

    if phys_accurate:
        geo

    if ax is None:
        ax = plt.gca()

    if projection.lower() == 'auto':
        projection = _automatic_projection_select(*geo)

    struct2D = tools.get_geometry_2d_projection(struct, projection=projection)
    struct2D = np.round(struct2D, 5)[:,0:2]

    if split : # split the structure along plane orthogonal to split_axis at split_value position
        struct1 = copy.deepcopy(struct)
        struct2 = copy.deepcopy(struct)
        
        if split_axis=='x' : 
            ind = 0
        elif split_axis=='y' : 
            ind = 1
        elif split_axis=='z' : 
            ind = 2
        else : print("Warning, wrong splitting axis value, must be among 'x','y','z'")
        separation_list_geo1 = []
        separation_list_geo2 = []
        for ipos,pos in enumerate(geo.T) : 
            if pos[ind]<split_value :
                separation_list_geo2.append(ipos)
            else : 
                separation_list_geo1.append(ipos)
    
        struct1.geometry = np.delete(geo.T, separation_list_geo1,0)
        struct2.geometry = np.delete(geo.T, separation_list_geo2,0)

        if projection.lower() == 'auto':
            projection = _automatic_projection_select(*geo)

        if phys_accurate : 
            if projection.lower() == 'xy':
                ind1, ind2 = 0,1
            elif projection.lower() == 'yz':
                ind1, ind2 = 1,2
            elif projection.lower() == 'xz':
                ind1, ind2 = 0,2

            struct1.geometry = _enlarge_struct_geometry(struct1.geometry, step/2, ind1,ind2,version=phys_enlarge_vers)
            struct2.geometry = _enlarge_struct_geometry(struct2.geometry, step/2, ind1,ind2,version=phys_enlarge_vers)

        struct2D1 = tools.get_geometry_2d_projection(struct1, projection=projection) #needs struct object to work, hence the copy procedure + replacement of each geometry
        struct2D2 = tools.get_geometry_2d_projection(struct2, projection=projection)
        struct2D1 = np.round(struct2D1, 5)[:,0:2]
        struct2D2 = np.round(struct2D2, 5)[:,0:2]

        edges1 = _alpha_shape(struct2D1, alpha=r_contour, only_outer=True)
        edges2 = _alpha_shape(struct2D2, alpha=r_contour, only_outer=True)

        # --- plot the contours
        plt.gca().set_aspect('equal')
        for i, j in edges1:
            ax.plot(struct2D1[[i, j], 0], struct2D1[[i, j], 1],color=color,lw=lw)
        for i, j in edges2:
            ax.plot(struct2D2[[i, j], 0], struct2D2[[i, j], 1],color=color,lw=lw)

    else : 
        if phys_accurate : 
            struct1 = copy.deepcopy(struct)
            if projection.lower() == 'xy':
                ind1, ind2 = 0,1
            elif projection.lower() == 'yz':
                ind1, ind2 = 1,2
            elif projection.lower() == 'xz':
                ind1, ind2 = 0,2
            struct1.geometry = _enlarge_struct_geometry(struct1.geometry, step/2, ind1,ind2,version=phys_enlarge_vers)
            struct2D = tools.get_geometry_2d_projection(struct1, projection=projection)
            struct2D = np.round(struct2D, 5)[:,0:2]

        edges = _alpha_shape(struct2D, alpha=r_contour, only_outer=True)
        ## --- plot the contours
        plt.gca().set_aspect('equal')
        for i, j in edges:
            cont = ax.plot(struct2D[[i, j], 0], struct2D[[i, j], 1], color=color, lw=lw, **kwargs)

    if tit:
        ax.set_title(tit)

    X = struct2D[:,0]
    Y = struct2D[:,1]
    if show: 
        ax.set_aspect("equal")
        ax.set_xlabel("{} (nm)".format(projection[0]))
        ax.set_ylabel("{} (nm)".format(projection[1]))
        ax.set_xlim(X.min()-borders*step, X.max()+borders*step)
        ax.set_ylim(Y.min()-borders*step, Y.max()+borders*step)
        plt.show()
    
    return cont
    


def structure_contour(struct, projection='auto', color='k',
                      alpha_value=None, lw=1, alpha=1.0, tit='',
                      set_ax_aspect=True, show=True, **kwargs):
    """Contour around structure via `alphashape`
    
    Requires the package `alphashape`.
    All further kwargs are passed to matplotlib's `ax.plot`.
    
    based on contribution by Simon Garrigou.
    
    Parameters
    ----------
    struct : list or :class:`.core.simulation` 
        either list of 3d coordinate tuples or simulation description object
    
    projection : str, default: 'auto'
        which 2D projection to plot: "auto", "XY", "YZ", "XZ"
    
    color : str or matplotlib color, default: "b"
        matplotlib-compatible color for scatter

    alpha_value : float, default: None
        optional manual value for alpha to calculate the concave hull. 
        By default, use 1/step.

    lw : float, default: 1
        linewidth as used by `pyplot.plot` (style='lines' only)

    alpha : float, default: 1.0
        matplotlib transparancy
        
    tit : str, default: ""
        title for plot (optional)
    
    set_ax_aspect : bool, default: True
        set canvas aspect ratio to equal
    
    show : bool, default: True
        directly show plot
    """
    import alphashape
    import logging

    logging.getLogger("alphashape").setLevel(logging.ERROR)

    
    geo = tools.get_geometry(struct)
    step = tools.get_step_from_geometry(struct)

    # prep
    ax, show = _get_axis_existing_or_new()
    if "show" in kwargs:
        show = kwargs.pop("show")
    if set_ax_aspect:
        ax.set_aspect("equal")

    # get geometry projection
    if projection.lower() == "auto":
        projection = _automatic_projection_select(*geo)
    
    pos_proj = tools.get_geometry_2d_projection(struct, projection=projection)
    pos_proj = np.round(pos_proj, 5)[:,:2]
    

    # expand geometry by a half-step (outer points)
    pos_px = pos_proj + np.array([[step / 2, step / 2]])
    pos_mx = pos_proj + np.array([[-step / 2, step / 2]])
    pos_py = pos_proj + np.array([[step / 2, -step / 2]])
    pos_my = pos_proj + np.array([[-step / 2, -step / 2]])
    pos2d_exp = np.concatenate([pos_px, pos_mx, pos_py, pos_my])

    # concave hull (alpha shape) - ignore warnings
    if alpha_value is None:
        alpha_value = 1.0 / step
    if type(alpha_value) == str:
        if alpha_value.lower() in ["opt", "optimize"]:
            alpha_value = _optimize_alpha_value(pos2d_exp)

    original_log_level = logging.getLogger().getEffectiveLevel()
    logging.disable(logging.WARN)
    geo_alpha = alphashape.alphashape(pos2d_exp, alpha_value)
    logging.disable(original_log_level)
    # maybe replace again by a simple local implementation to avoid dependencies
    # edges = _alpha_shape(pos2d_exp, alpha_value)

    if geo_alpha.geom_type == "Polygon":
        g_a_list = [geo_alpha]
    elif geo_alpha.geom_type == "MultiPolygon":
        g_a_list = [_g for _g in geo_alpha.geoms]
    else:
        raise ValueError("Unexpected error: Unknown alphashape geometry.")

    for _geo_a in g_a_list:
        # plot every sub geometry
        xx, yy = _geo_a.exterior.coords.xy
        xx, yy = xx.tolist(), yy.tolist()
        ax.plot(xx, yy, color=color, alpha=alpha, lw=lw, **kwargs)

    ax.autoscale(tight=False)
    
    if show:
        ax.set_xlabel("{} (nm)".format(projection[0]))
        ax.set_ylabel("{} (nm)".format(projection[1]))
        plt.show()


    # # concave hull (alpha shape)
    # alpha_shape = alphashape.alphashape(pos2d_exp, alpha_value)
    # xx, yy = alpha_shape.exterior.coords.xy
    # xx, yy = xx.tolist(), yy.tolist()

    # # plot
    # ax.plot(xx, yy, color=color, alpha=alpha, **kwargs)
    # ax.autoscale(tight=False)
    # ax.set_xlabel("{} (nm)".format(projection[0]))
    # ax.set_ylabel("{} (nm)".format(projection[1]))
    if tit:
        plt.title(tit)
    # if show:
    #     plt.show()
    
    
    
    return ax

##----------------------------------------------------------------------
##                     INTERNAL FIELD - FUNDAMENTAL
##----------------------------------------------------------------------
def vectorfield(NF, struct=None, projection='auto', complex_part='real', 
                tit='',
                slice_level=None,
                scale=10.0, vecwidth=1.0, cmap=cm.Blues, cmin=0.3, 
                ax=None, adjust_axis=True, set_ax_aspect=True, 
                borders=3, EACHN=1, sortL=True, overrideMaxL=False, 
                **kwargs):
    """plot 2D Vector field as quiver plot
    
    plot nearfield list as 2D vector plot, using matplotlib's `quiver`.
    `kwargs` are passed to `pyplot.quiver`
    
    Parameters
    ----------
    NF : list of 3- or 6-tuples
        Nearfield definition. `np.array`, containing 6-tuples:
        (X,Y,Z, Ex,Ey,Ez), the field components being complex (use e.g. 
        :func:`.tools.get_field_as_list`). 
        Optionally can also take a list of 3-tuples (Ex, Ey, Ez), 
        in which case the structure must be provided via the `struct` kwarg. 
                   
    struct : list or :class:`.core.simulation`, optional
        optional structure definition (necessary if field is supplied in 
        3-tuple form without coordinates). Either `simulation` description 
        object, or list of (x,y,z) coordinate tuples 
                 
    projection : str, default: 'auto'
        Which 2D projection to plot: "auto", "XY", "YZ", "XZ"
     
    complex_part : str, default: 'real'
        Which part of complex field to plot. Either 'real' or 'imag'. 
                     
    tit : str, default: ""
        title for plot (optional)
     
    slice_level: float, default: `None`
        optional value of depth where to slice. eg if projection=='XY', 
        slice_level=10 will take only values where Z==10.
            - slice_level = `None`, plot all vectors one above another without slicing.
            - slice_level = -9999 : take minimum value in field-list.
            - slice_level = 9999 : take maximum value in field-list.
    
    scale : float, default: 10.0
        optional vector length scaling parameter
     
    vecwidth : float, default: 1.0
        optional vector width scaling parameter
     
    cmap : matplotlib colormap, default: `cm.Blues`
        matplotlib colormap to use for arrows (color scaling by vector length)
     
    cmin : float, default: 0.3
        minimal color to use from cmap to avoid pure white
     
    ax : matplotlib `axes`, default: None (=create new)
        optinal axes object (mpl) to plot into
    
    adjust_axis : bool, default: True
        apply adjustments to axis (equal aspect, axis labels, plot-range)
    
    set_ax_aspect : bool, default: True
        set canvas aspect ratio to equal
    
    borders : float, default: 3
          additional space limits around plot in units of stepsize
     
    EACHN : int, default: 1 [=all]
        show each N points only
     
    sortL : bool, default: True
        sort vectors by length to avoid clipping (True: Plot longest 
        vectors on top)
     
    overrideMaxL : bool, default: False
        if True, use 'scale' as absolute scaling. Otherwise, normalize to 
        field-vector amplitude.
     
    Returns
    -------
    
    return value of matplotlib's `quiver`
    
    """
    # prep
    ax, show = _get_axis_existing_or_new()
    if "show" in kwargs:
        show = kwargs.pop("show")
    if set_ax_aspect:
        ax.set_aspect("equal")
    
    NF_plt = copy.deepcopy(NF)
    if len(NF) == 2:
        NF_plt = NF_plt[1]
    
    if len(NF_plt.T) == 6:
        X,Y,Z, UXcplx,UYcplx,UZcplx = np.transpose(NF_plt)
    elif len(NF_plt.T) == 3 and struct is not None:
        UXcplx,UYcplx,UZcplx = np.transpose(NF_plt)
        X,Y,Z = tools.get_geometry(struct)
    else:
        raise ValueError("Error: Wrong number of columns in vector field. Expected (Ex,Ey,Ez)-tuples + `simulation` object or (x,y,z, Ex,Ey,Ez)-tuples.")
    
    X = np.real(X)
    Y = np.real(Y)
    Z = np.real(Z)
    step = tools.get_step_from_geometry(np.transpose([X,Y,Z]))
    
    if projection.lower() == 'auto':
        projection = _automatic_projection_select(X,Y,Z)
    
    if complex_part.lower() == "real":
        UX, UY, UZ = UXcplx.real, UYcplx.real, UZcplx.real
    elif complex_part.lower() == "imag":
        UX, UY, UZ = UXcplx.imag, UYcplx.imag, UZcplx.imag
    else:
        raise ValueError("Error: Unknown `complex_part` argument value. Must be either 'real' or 'imag'.")
    
    if projection.lower() == 'xy':
        SLICE = copy.deepcopy(Z)
        X=X[::EACHN].real; Y=Y[::EACHN].real
        UX=UX[::EACHN]; UY=UY[::EACHN]
    elif projection.lower() == 'yz':
        SLICE = copy.deepcopy(X)
        X=Y[::EACHN].real; Y=Z[::EACHN].real
        UX=UY[::EACHN]; UY=UZ[::EACHN]
    elif projection.lower() == 'xz':
        SLICE = copy.deepcopy(Y)
        X=X[::EACHN].real; Y=Z[::EACHN].real
        UX=UX[::EACHN]; UY=UZ[::EACHN]
    else:
        raise ValueError("Invalid projection parameter!")
    
    
    ## -- optional slicing
    if slice_level is not None:
        slice_level_closest = np.unique(SLICE)[np.argmin(np.abs(np.unique(SLICE) - slice_level))]
        if slice_level_closest != slice_level:
            if np.abs(slice_level) != 9999:
                warnings.warn("slice level at {}nm contains no meshpoints. Using closest level containing meshpoint at {}nm".format(
                                              slice_level, slice_level_closest))
            slice_level = slice_level_closest
    
        X, Y   = X[(SLICE == slice_level)], Y[(SLICE == slice_level)]
        UX, UY = UX[(SLICE == slice_level)], UY[(SLICE == slice_level)]
    
    
    ## -- sort and scale by length
    def sortbylength(X,Y,EX,EY):
        ## -- sort by vector length to plot short vectors above long ones
        DATARR = []
        for i, (xi, yi, pxi, pyi) in enumerate(zip(X,Y,EX,EY)):
            DATARR.append([(pxi**2+pyi**2),xi,yi,pxi,pyi])
        
        DATARR = np.transpose(sorted(DATARR))
        
        X = DATARR[1]
        Y = DATARR[2]
        UX = DATARR[3]
        UY = DATARR[4]
        
        return X,Y,UX,UY  
    if sortL:
        X,Y,UX,UY = sortbylength(X,Y,UX,UY)
    
    
    ## vector length
    LenALL = np.sqrt(UX**2 + UY**2)   # absolute scaling
    
    
    if not overrideMaxL:
        scale = scale * LenALL.max()
    else:
        scale = scale
    
    ## -- quiver plot
    vecwidth = vecwidth * 0.005
    cscale = mcolors.Normalize( LenALL.min()-cmin*(LenALL.max()-LenALL.min()), 
                                LenALL.max())   # cmap colors by vector length
    
    if ax != None:
        if tit:
            ax.set_title(tit)
        im = ax.quiver(X,Y, UX,UY, scale=scale, 
                       width=vecwidth, color=cmap(cscale(LenALL)), **kwargs)
    else:
        if tit:
            plt.title(tit)
        im = plt.quiver(X,Y, UX,UY, scale=scale, 
                        width=vecwidth, color=cmap(cscale(LenALL)), **kwargs)
        ax = plt.gca()
        
    if adjust_axis:
        ax.set_xlim(X.min() - borders*step, X.max() + borders*step)
        ax.set_ylim(Y.min() - borders*step, Y.max() + borders*step)
        ax.set_xlabel("{} (nm)".format(projection[0]))
        ax.set_ylabel("{} (nm)".format(projection[1]))
    
    if show: 
        plt.show()
    
    return im


def vectorfield_by_fieldindex(sim, field_index, which_field='E', **kwargs):
    """Wrapper to :func:`.vectorfield`, using simulation object and fieldindex as input
    
    All other keyword arguments are passed to :func:`.vectorfield`.
    
    Parameters
    ----------
    sim : `simulation`
        instance of :class:`.core.simulation`
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    which_field : str, default: "E"
        "E" or "H", for electric or magnetic field
        
    """
    NF = tools.get_field_as_list_by_fieldindex(sim, field_index, which_field)
    return vectorfield(NF, **kwargs)






def vectorfield_fieldlines(NF, struct=None, projection='auto', tit='', 
                           complex_part='real', borders=0,
                           NX=-1, NY=-1, set_ax_aspect=True, **kwargs):
    """2d plot of fieldlines of field 'NF'
    
    other optional arguments passed to matplotlib's `pyplot.streamplot`
    
    Parameters
    ----------
    NF : list of 3- or 6-tuples
        Nearfield definition. `np.array`, containing 6-tuples:
        (X,Y,Z, Ex,Ey,Ez), the field components being complex (use e.g. 
        :func:`.tools.get_field_as_list`). 
        Optionally can also take a list of 3-tuples (Ex, Ey, Ez), 
        in which case the structure must be provided via the `struct` kwarg. 
                   
    struct : list or :class:`.core.simulation`, optional
        optional structure definition (necessary if field is supplied in 
        3-tuple form without coordinates). Either `simulation` description 
        object, or list of (x,y,z) coordinate tuples 
    
    projection : str, default: 'XY'
        Which projection to plot: "XY", "YZ", "XZ"
     
    complex_part : str, default: 'real'
        Which part of complex field to plot. Either 'real' or 'imag'. 
                     
    tit : str, default: ""
        title for plot (optional)
        
    borders : float, default: 0
          additional space limits around plot in units of stepsize
     
    NX, NY : int, int, defaults: -1, -1
        optional interpolation steps for nearfield. 
        by default take number of independent positions in NF 
        (if NX or NY == -1)
    
    set_ax_aspect : bool, default: True
        set canvas aspect ratio to equal
    
    Returns
    -------
        matplotlib `streamplot` object
    """
    # prep
    ax, show = _get_axis_existing_or_new()
    if "show" in kwargs:
        show = kwargs.pop("show")
    if set_ax_aspect:
        ax.set_aspect("equal")
    
    NF_plt = copy.deepcopy(NF)
    if len(NF) == 2:
        NF_plt = NF_plt[1]
    
    if len(NF_plt.T) == 6:
        X,Y,Z, Ex,Ey,Ez = np.transpose(NF_plt)
    elif len(NF_plt.T) == 3 and struct is not None:
        Ex,Ey,Ez = np.transpose(NF_plt)
        X,Y,Z = tools.get_geometry(struct)
    else:
        raise ValueError("Error: Wrong number of columns in vector field. Expected (Ex,Ey,Ez)-tuples + `simulation` object or (x,y,z, Ex,Ey,Ez)-tuples.")
    
    x = np.real(X)
    y = np.real(Y)
    z = np.real(Z)
    step = tools.get_step_from_geometry(np.transpose([x,y,z]))
        
    if projection.lower() == 'auto':
        projection = _automatic_projection_select(x, y, z)
    
    if complex_part.lower() == "real":
        Ex, Ey, Ez = Ex.real, Ey.real, Ez.real
    elif complex_part.lower() == "imag":
        Ex, Ey, Ez = Ex.imag, Ey.imag, Ez.imag
    else:
        raise ValueError("Error: Unknown `complex_part` argument value. " + 
                         "Must be either 'real' or 'imag'.")
    
    
    if projection.lower() == 'xy':
        X=x; Y=y; EX=Ex; EY=Ey
    if projection.lower() == 'xz':
        X=x; Y=z; EX=Ex; EY=Ez
    if projection.lower() == 'yz':
        X=y; Y=z; EX=Ey; EY=Ez
    
    X = np.unique(X)
    Y = np.unique(Y)
    
    if NX == -1:
        NX = len(X)
    if NY == -1:
        NY = len(Y)
    
    MAP_XY = tools.generate_NF_map(np.min(X),np.max(X),NX, np.min(Y),np.max(Y),NY)
    
    NF_X, _extent = tools.list_to_grid(np.transpose([MAP_XY.T[0], MAP_XY.T[1], EX]))
    NF_Y, _extent = tools.list_to_grid(np.transpose([MAP_XY.T[0], MAP_XY.T[1], EY]))
    
    strplt = plt.streamplot(X, Y, NF_X, NF_Y, **kwargs)
    
    plt.xlim(_extent[0]-borders*step, _extent[1]+borders*step)
    plt.ylim(_extent[2]-borders*step, _extent[3]+borders*step)
    
    if show:
        if tit:
            plt.title(tit)
        plt.gca().set_aspect("equal")
        plt.xlabel("{} (nm)".format(projection[0]))
        plt.ylabel("{} (nm)".format(projection[1]))
        plt.show()
    
    return strplt



## 2D colorplot
def vectorfield_color(NF, struct=None, projection='auto', complex_part='real', 
                      tit='', ax=None, 
                      slice_level=-9999, NX=None, NY=None, fieldComp='I', 
                      borders=0, clim=None, grid_interpolation='linear',
                      set_ax_aspect=True, return_map_array=False,
                      **kwargs):
    """plot of 2D field data as colorplot
    
    other kwargs are passed to matplotlib's `imshow`
    
    Parameters
    ----------
    NF : list of 3- or 6-tuples
        Nearfield definition. `np.array`, containing 6-tuples:
        (X,Y,Z, Ex,Ey,Ez), the field components being complex (use e.g. 
        :func:`.tools.get_field_as_list`). 
        Optionally can also take a list of 3-tuples (Ex, Ey, Ez), 
        in which case the structure must be provided via the `struct` kwarg. 
                   
    struct : list or :class:`.core.simulation`, optional
        optional structure definition (necessary if field is supplied in 
        3-tuple form without coordinates). Either `simulation` description 
        object, or list of (x,y,z) coordinate tuples 
    
    projection : str, default: 'auto'
        which 2D projection to plot: "auto", "XY", "YZ", "XZ"
     
    complex_part : str, default: 'real'
        Which part of complex field to plot. Either 'real' or 'imag'. 
                     
    tit : str, default: ""
        title for plot (optional)
    
    ax : matplotlib `axes`, default: None (=create new)
        DEPRECATED, does nothing. optional axes object (mpl) to plot into
    
    slice_level: float, default: `None`
        optional value of depth where to slice. eg if projection=='XY', 
        slice_level=10 will take only values where Z==10.
            - slice_level = `None`, plot all vectors one above another without slicing.
            - slice_level = -9999 : take minimum value in field-list.
            - slice_level = 9999 : take maximum value in field-list.
    
    NX, NY : int, int, defaults: None, None
        optional interpolation steps for nearfield. 
        by default take number of independent positions in NF 
        (if NX or NY == None)
     
    fieldComp : str, default: 'I'
        Which component to use. One of ["I", "abs", "Ex", "Ey", "Ez"].
        If one of "I" or "abs" is used, `complex_part` argument has no effect.
                    
    borders : float, default: 0
        additional space in nm to plotting borders
        
    cmap : matplotlib colormap, default: "seismic"
        matplotlib colormap to use for colorplot
     
    clim : float, default: None
        optional colormap limits to pass to `plt.clim()`
     
    grid_interpolation : str, default: 'linear'
        interpolation method for scipy `grid_data`. Can be 'linear' or 'nearest'.
        See `scipy.interpolate.griddata` for details
     
    return_map_array : bool, default: False    
        if true, returns tuyple (im, arr). `im` is matplotlib object, `arr` the data-array generated for `plt.imshow`
    
    set_ax_aspect : bool, default: True
        set canvas aspect ratio to equal
    
    
    Returns
    -------
        result of matplotlib's `imshow` and optionally the 2D ploted data as numpy array
    """
    # prep
    ax, show = _get_axis_existing_or_new()
    if "show" in kwargs:
        show = kwargs.pop("show")
    if set_ax_aspect:
        ax.set_aspect("equal")
    
    NF_plt = copy.deepcopy(NF)
    if len(NF) == 2:
        NF_plt = NF_plt[1]
    
    if len(NF_plt.T) == 6:
        X,Y,Z, Ex,Ey,Ez = np.transpose(NF_plt)
    elif len(NF_plt.T) == 3 and struct is not None:
        Ex,Ey,Ez = np.transpose(NF_plt)
        X,Y,Z = tools.get_geometry(struct)
    else:
        raise ValueError("Error: Wrong number of columns in vector field. Expected (Ex,Ey,Ez)-tuples + `simulation` object or (x,y,z, Ex,Ey,Ez)-tuples.")
    
    X = np.real(X)
    Y = np.real(Y)
    Z = np.real(Z)
    step = tools.get_step_from_geometry(np.transpose([X,Y,Z]))
    
    if projection.lower() == 'auto':
        projection = _automatic_projection_select(X,Y,Z)
    
    if fieldComp.lower() not in ['i', 'abs']:
        if complex_part.lower() == "real":
            Ex, Ey, Ez = Ex.real, Ey.real, Ez.real
        elif complex_part.lower() == "imag":
            Ex, Ey, Ez = Ex.imag, Ey.imag, Ez.imag
        else:
            raise ValueError("Error: Unknown `complex_part` argument value." +
                             " Must be either 'real' or 'imag'.")
    
    
    if fieldComp.lower() in ['i', 'abs']:
        EF = np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2
        if fieldComp.lower() == 'abs':
            EF = np.sqrt(EF)
    elif fieldComp.lower() == 'ex':
        EF = Ex
    elif fieldComp.lower() == 'ey':
        EF = Ey
    elif fieldComp.lower() == 'ez':
        EF = Ez
    
    
    ## map / slicing
    if projection.lower() == 'xy':
        SLICE = copy.deepcopy(Z)
    if projection.lower() == 'xz':
        SLICE = copy.deepcopy(Y)
    if projection.lower() == 'yz':
        SLICE = copy.deepcopy(X)
        
    slice_level_closest = np.unique(SLICE)[np.argmin(np.abs(np.unique(SLICE) - slice_level))]
    if slice_level_closest != slice_level:
        if np.abs(slice_level) != 9999:
            warnings.warn("slice level Z={} contains no meshpoints. Using closest level containing meshpoint at Z={}".format(
                                          slice_level, slice_level_closest))
        slice_level = slice_level_closest
    if projection.lower() == 'xy':
        XYZList = np.transpose([X[(SLICE == slice_level)],Y[(SLICE == slice_level)], EF[(SLICE == slice_level)]])
    if projection.lower() == 'xz':
        XYZList = np.transpose([X[(SLICE == slice_level)],Z[(SLICE == slice_level)], EF[(SLICE == slice_level)]])
    if projection.lower() == 'yz':
        XYZList = np.transpose([Y[(SLICE == slice_level)],Z[(SLICE == slice_level)], EF[(SLICE == slice_level)]])
    
    
    MAP, extent = tools.list_to_grid(XYZList, NX, NY, interpolation=grid_interpolation)
    
    if tit: ax.set_title(tit)
    img = ax.imshow(MAP, extent=extent, **kwargs)
    if clim: img.set_clim(clim)
    
    ax.set_xlim(extent[0] - borders*step, extent[1] + borders*step)
    ax.set_ylim(extent[2] - borders*step, extent[3] + borders*step)
    
    if show: 
        if fieldComp.lower() == 'i':
            plt.colorbar(img, label=r'$|E|^2 / |E_0|^2$')
        else:
            plt.colorbar(img, label=r'$E / |E_0|$')
        ax.set_aspect("equal")
        ax.set_xlabel("{} (nm)".format(projection[0]))
        ax.set_ylabel("{} (nm)".format(projection[1]))
        plt.show()
    if return_map_array:
        return img, MAP
    else:
        return img
    


def vectorfield_color_by_fieldindex(sim, field_index, which_field='E',
                                    grid_interpolation='nearest', **kwargs):
    """Wrapper to :func:`.vectorfield_color`, using simulation object and fieldindex as input
    
    All other keyword arguments are passed to :func:`.vectorfield_color`.
    
    Parameters
    ----------
    sim : `simulation`
        instance of :class:`.core.simulation`
    
    field_index : int
        index of evaluated self-consistent field to use for calculation. Can be
        obtained for specific parameter-set using :func:`.tools.get_closest_field_index`
    
    grid_interpolation : str, default: 'nearest'
        interpolation method for scipy `grid_data`. Can be 'linear' or 'nearest'.
        See `scipy.interpolate.griddata` for details
    
    which_field : str, default: "E"
        "E" or "H", for electric or magnetic field
        
    """
    NF = tools.get_field_as_list_by_fieldindex(sim, field_index, which_field, full_volume=True)
    
    return vectorfield_color(NF, grid_interpolation=grid_interpolation, **kwargs)


def scalarfield(NF, **kwargs):
    """Wrapper to :func:`.vectorfield_color`, using scalar data tuples (x,y,z,S) as input
    
    All other keyword arguments are passed to :func:`.vectorfield_color`.
    
    Parameters
    ----------
    NF : list of 4-tuples
        list of tuples (x,y,z,S). 
        Alternatively, the scalar-field can be passed as list of 2 lists 
        containing the x/y positions and scalar values, respectively.
        ([xy-values, S], with xy-values: list of 2-tuples [x,y]; S: list of 
        scalars). This format is returned e.g. by 
        :func:`.tools.calculate_rasterscan`.
    
    """
    if len(NF) == 2 and np.shape(NF[0])[1] == 2 and len(np.shape(NF[1])) == 1 \
                    and len(NF[0]) == len(NF[1]):
        NF = np.concatenate([NF[0].T, [np.zeros(len(NF[1]))], [NF[1]]]).T
    elif len(NF.T) != 4:
        NF = np.array(NF).T
        if len(NF.T) != 4:
            raise ValueError("Error: Scalar field must consist of 4-tuples (x,y,z,S).")
    NF = np.array(NF)
    
    x, y, z = NF.T[0:3]
    Ex = Ey = Ez = NF.T[3]
    NF = np.transpose([x,y,z, Ex,Ey,Ez])
    
    im = vectorfield_color(NF, complex_part='real', fieldComp='Ex', **kwargs)
    return im








##----------------------------------------------------------------------
##               FARFIELD (INTENSITY)
##----------------------------------------------------------------------
def farfield_pattern_2D(theta, phi, I, degrees=True,
                        show=True, ax=None, **kwargs):
    """Plot BFP-like 2D far-field radiation pattern
    
    Plot a "back-focal plane"-like radiation pattern.
    All arrays are of shape (Nteta, Nphi)
    
    kwargs are passed to matplotlib's `pyplot.pcolormesh`.
    
    Parameters
    ----------
    tetalist : 2D-`numpy.ndarray`, float
        teta angles
    
    philist : 2D-`numpy.ndarray`, float
        phi angles
    
    Iff : 2D-`numpy.ndarray`, float
        Intensities at (teta, phi) positions
    
    degrees : bool, default: True
        Transform polar angle to degrees for plotting (False: radians)
    
    ax : matplotlib `axes`, default: None (=create new)
        optinal axes object (mpl) to plot into
    
    show : bool, default: True
        whether to call `pyplot.show()`
    
    
    Returns
    -------
        result of matplotlib's `pyplot.pcolormesh`
    """
    if ax is None:
        ax = plt.gca()
        if ax.name == 'polar':
            pass
        else:
            ax = plt.subplot(polar=True)
        
    Nteta, Nphi = I.shape
    
    ## --- for plotting only: Add 360degrees (copy of 0 degrees)
    teta = np.concatenate([theta.T, [theta.T[-1]]]).T
    phi = np.concatenate([phi.T, [np.ones(phi.T[-1].shape) * 2*np.pi]]).T - np.pi/float(Nphi)
    I = np.concatenate([I.T, [I.T[-1]]]).T
    
    ## --- other parameters
    if degrees:
        conv_factor = 180./np.pi
    else:
        conv_factor = 1 
    
    if 'edgecolors' not in kwargs:
        kwargs['edgecolors']='face'
        
    ## --- plot
    im = ax.pcolormesh(phi, teta*conv_factor, I, **kwargs)
    
    if show:
        plt.colorbar(im, ax=ax)
        plt.show()
    
    return im







##----------------------------------------------------------------------
##               Oszillating Field Animation
##----------------------------------------------------------------------
def animate_vectorfield(NF, struct=None, Nframes=50, projection='auto', doQuiver=True, doColor=False, 
                     alphaColor=1.0, scale=5., clim=None,
                     kwargs={'cmin':0.3}, kwargsColor={'fieldComp':'Ex'}, ax=None, 
                     t_start=0, frame_list=None, show=True):
    """Create animation of oszillating complex nearfield (2D-Projection)
    
    Parameters
    ----------
    NF : list of 3- or 6-tuples
        Nearfield definition. `np.array`, containing 6-tuples:
        (X,Y,Z, Ex,Ey,Ez), the field components being complex (use e.g. 
        :func:`.tools.get_field_as_list`). 
        Optionally can also take a list of 3-tuples (Ex, Ey, Ez), 
        in which case the structure must be provided via the `struct` kwarg. 
                   
    struct : list or :class:`.core.simulation`, optional
        optional structure definition (necessary if field is supplied in 
        3-tuple form without coordinates). Either `simulation` description 
        object, or list of (x,y,z) coordinate tuples 
      
    Nframes : int, default: 50
          number of frames per oscillation cycle 
      
    projection : str, default: 'auto'
        which 2D projection to plot: "auto", "XY", "YZ", "XZ"
      
    doQuiver : bool, default: True
          plot field as quiverplot. 
      
    doColor : bool, default: True
          plot field as colorplot (real part)
      
    alphaColor : float, default: 0.5
          alpha value of colormap
          
    kwargs : dict, default: {}
          are passed to :func:`.vectorfield` (if doQuiver)
      
    kwargsColor : dict, default: {}
          are passed to :func:`.vectorfield_color` (if doColor)
      
    ax : optional matplotlib `axes`, default: None
          optional axes object (mpl) to plot into

    t_start : int, default: 0
        time-step to start animation at (=frame number)
        
    frame_list : list, default: None
        optional list of frame indices to use for animation. Can be used to 
        animate only a part of the time-harmonic cycle.
    
    show : bool, default: True
          directly show animation 

    Returns
    -------
        im_ani : Animation as matplotlib "ArtistAnimation" object
      
     
    Notes
    -----
        You can save the animation as video-file using: 
        im_ani.save('video.mp4', writer="ffmpeg", codec='h264', bitrate=1500).
        See also matplotlib's documentation of the `animation` module for more info.
      
    """
    NF_plt = copy.deepcopy(NF)
    if len(NF) == 2:
        NF_plt = NF_plt[1]
    
    if len(NF_plt.T) == 6:
        X,Y,Z, Ex,Ey,Ez = np.transpose(NF_plt)
    elif len(NF_plt.T) == 3 and struct is not None:
        Ex,Ey,Ez = np.transpose(NF_plt)
        X,Y,Z = tools.get_geometry(struct)
    else:
        raise ValueError("Error: Wrong number of columns in vector field. Expected (Ex,Ey,Ez)-tuples + `simulation` object or (x,y,z, Ex,Ey,Ez)-tuples.")
    
    x = np.real(X)
    y = np.real(Y)
    z = np.real(Z)
    
    
    if projection.lower() == 'auto':
        projection = _automatic_projection_select(x,y,z)
    
    ## get phase and length of complex field
    Exi = Ex
    Exr = np.absolute(Exi)
    Ax  = np.angle(Exi)
    
    Eyi = Ey
    Eyr = np.absolute(Eyi)
    Ay  = np.angle(Eyi)
    
    Ezi = Ez
    Ezr = np.absolute(Ezi)
    Az  = np.angle(Ezi)
    
    scaleF = float((Exr.max()+Eyr.max()+Ezr.max()))
    Exr /= scaleF
    Eyr /= scaleF
    Ezr /= scaleF
    
    ## create list of timesteps
    import matplotlib.pyplot as plt
    alambda = 100
    omega = 2*np.pi/alambda
    
    if show:
        fig = plt.figure()
    else: fig = plt.gcf()
    
    ax = ax or plt.subplot(aspect="equal")
    
    framnumbers = np.linspace(t_start, alambda+t_start, Nframes)
    if frame_list is not None:
        framnumbers = framnumbers[frame_list]
    
    ims = []
    for t in framnumbers:
        plotlist = []
        NF_plt = np.transpose([x,y,z, (Exr * np.exp(1j*(Ax - omega*t))),
                                      (Eyr * np.exp(1j*(Ay - omega*t))),
                                      (Ezr * np.exp(1j*(Az - omega*t)))])
        if doColor:
            pt2 = vectorfield_color(NF_plt, alpha=alphaColor, projection=projection, 
                                    show=False, clim=clim, **kwargsColor)
            plotlist.append(pt2)        
        if doQuiver:
            pt1 = vectorfield(NF_plt, projection=projection, scale=scale, 
                              overrideMaxL=True, show=False, **kwargs)
            plotlist.append(pt1)
        
        ims.append( tuple(plotlist) )


    import matplotlib.animation as animation
    im_ani = animation.ArtistAnimation(fig, ims, interval=50, repeat_delay=0,
                                       blit=True, repeat=True)
    
    if show:
        plt.show()
    
    return im_ani









