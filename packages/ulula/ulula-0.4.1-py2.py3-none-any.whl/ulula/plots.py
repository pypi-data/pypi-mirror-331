###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

import ulula.utils.utils as utils

###################################################################################################

fields = {}
"""
List of fields that can be plotted. Most fields occur in the primitive or conserved variable 
arrays, but some fields are derived (e.g., total velocity).
"""

fields['DN']       = {'name': 'Density',        'label': r'\rho',                 'cmap': 'viridis'}
fields['VX']       = {'name': 'X-velocity',     'label': r'v_{\rm x}',             'cmap': 'RdBu_r'}
fields['VY']       = {'name': 'Y-velocity',     'label': r'v_{\rm y}',             'cmap': 'RdBu_r'}
fields['VT']       = {'name': 'Total velocity', 'label': r'v_{\rm tot}',           'cmap': 'viridis'}
fields['PR']       = {'name': 'Pressure',       'label': r'P',                     'cmap': 'viridis'}
fields['MX']       = {'name': 'X-momentum',     'label': r'm_{\rm x}',            'cmap': 'RdBu_r'}
fields['MY']       = {'name': 'Y-momentum',     'label': r'm_{\rm y}',             'cmap': 'RdBu_r'}
fields['ET']       = {'name': 'Energy',         'label': r'E',                     'cmap': 'viridis'}
fields['GP']       = {'name': 'Potential',      'label': r'\Phi',                 'cmap': 'viridis'}
fields['GX']       = {'name': 'Pot. gradient',  'label': r'{\rm d}\Phi/{\rm d}x', 'cmap': 'RdBu_r'}
fields['GY']       = {'name': 'Pot. gradient',  'label': r'{\rm d}\Phi/{\rm d}y', 'cmap': 'RdBu_r'}

label_code_units = r'{\rm CU}'

###################################################################################################

def getPlotQuantities(sim, q_plot, unit_l = 'code', unit_t = 'code', unit_m = 'code'):
    """
    Compile an array of fluid properties
    
    Fluid properties are stored in separate arrays as primitive and conserved variables, or
    even in other arrays. Some quantities, such as total velocity, need to be calculated after
    the simulation has finished. This function takes care of all related operations and returns
    a single array that has the same dimensions as the domain. 
    
    Moreover, the function computes unit conversion factors if necessary and creates the 
    corresponding labels.
    
    Parameters
    ----------
    sim: Simulation
        Object of type :data:`~ulula.simulation.Simulation`
    q_plot: array_like
        List of quantities to plot. Quantities are identified via the short strings given in the
        :data:`~ulula.plots.fields` dictionary.
    unit_l: str
        Length unit to be plotted (see :data:`~ulula.utils.utils.units_l` for valid units). If other 
        than ``code``, ``unit_t`` and ``unit_m`` must also be changed from code units.
    unit_t: str
        Time unit to be plotted (see :data:`~ulula.utils.utils.units_t` for valid units). If other 
        than ``code``, ``unit_l`` and ``unit_m`` must also be changed from code units.
    unit_m: str
        Mass unit to be plotted (see :data:`~ulula.utils.utils.units_m` for valid units). If other 
        than ``code``, ``unit_l`` and ``unit_t`` must also be changed from code units.

    Returns
    -------
    q_array: array_like
        Array of fluid properties
    conv_factors: array_like
        Unit conversion factors. The return ``q_array`` has already been multiplied by these factors
        in order to bring it into the desired unit system, but some other parts of the plot
        routines (e.g., color map limits) may also depend on these factors. If the plotting happens
        in code units, all factors are unity.
    q_labels: array_like
        List of labels for the fluid quantities
    conv_l: float
        Unit conversion factor for length, which must be applied to the dimensions of any plot.
    label_l: float
        Unit label for lengths.
    """
    
    # Check that quantities are valid
    for q in q_plot:
        if not q in fields:
            raise Exception('Unknown quantity, %s. Valid quantities are %s.' \
                        % (str(q), str(list(fields.keys()))))

    nq = len(q_plot)
    q_array = np.zeros((nq, sim.nx + 2 * sim.nghost, sim.ny + 2 * sim.nghost), float)
    conv_factors = []
    q_labels = []

    # If we are converting units, we compute conversion factors between code units and the given
    # units once before applying them to all plotted quantities. We do not allow a mixture of
    # code and other units, since this becomes complicated for mixed quantities (e.g., density in
    # tons / code unit^3 are not intuitive). 
    do_convert = ((unit_l != 'code') or (unit_t != 'code') or (unit_m != 'code'))
    if do_convert:
        conv_l = 1.0
        conv_t = 1.0
        conv_m = 1.0
        if ((unit_l == 'code') or (unit_t == 'code') or (unit_m == 'code')):
            raise Exception('Found mixed code and other units (%s, %s, %s). Please select consistent unit system.' \
                        % (unit_l, unit_t, unit_m))
        if not unit_l in utils.units_l:
            raise Exception('Unknown length unit, %s. Allowed are %s.' % (unit_l, str(list(utils.units_l.keys()))))
        conv_l = sim.unit_l / utils.units_l[unit_l]['in_cgs']
        unit_label_l = utils.units_l[unit_l]['label']
        
        if not unit_t in utils.units_t:
            raise Exception('Unknown time unit, %s. Allowed are %s.' % (unit_t, str(list(utils.units_t.keys()))))
        conv_t = sim.unit_t / utils.units_t[unit_t]['in_cgs']
        unit_label_t = utils.units_t[unit_t]['label']

        if not unit_m in utils.units_m:
            raise Exception('Unknown mass unit, %s. Allowed are %s.' % (unit_m, str(list(utils.units_m.keys()))))
        conv_m = sim.unit_m / utils.units_m[unit_m]['in_cgs']
        unit_label_m = utils.units_m[unit_m]['label']
    else:
        conv_l = 1.0
        unit_label_l = label_code_units

    # Copy quantities from the simulation, and compute them if necessary
    for iq in range(nq):
        q = q_plot[iq]
        if q in sim.q_prim:
            q_array[iq] = sim.V[sim.q_prim[q]]
        elif q in sim.q_cons:
            q_array[iq] = sim.U[sim.q_cons[q]]
        elif q == 'VT':
            q_array[iq] = np.sqrt(sim.V[sim.q_prim['VX']]**2 + sim.V[sim.q_prim['VY']]**2)
        else:
            raise Exception('Unknown quantity, %s.' % (str(q)))
        
        # Convert units and create combined labels, if necessary
        if do_convert:
            if q in ['DN']:
                conv_fac = conv_m / conv_l**3
                unit_label = unit_label_m + r'/' + unit_label_l + r'^3'
            elif q in ['VX', 'VY', 'VT']:
                conv_fac = conv_l / conv_t
                unit_label = unit_label_l + r'/' + unit_label_t
            elif q in ['PR', 'ET']:
                conv_fac = conv_m / conv_l / conv_t**2
                unit_label = unit_label_m + r'/' + unit_label_l + r'/' + unit_label_t + r'^2'
            elif q in ['MX', 'MY']:
                conv_fac = conv_m / conv_l**2 / conv_t
                unit_label = unit_label_m + r'/' + unit_label_l + r'^2/' + unit_label_t
            elif q in ['GP']:
                conv_fac = conv_l**2 / conv_t**2
                unit_label = unit_label_l + r'^2/' + unit_label_t + r'^2'
            elif q in ['GX', 'GY']:
                conv_fac = conv_l / conv_t**2
                unit_label = unit_label_l + r'/' + unit_label_t + r'^2'
            else:
                raise Exception('Could not find conversion for plot quantity %s.' % (q))
            q_array[iq] *= conv_fac
            conv_factors.append(conv_fac)
        else:
            unit_label = label_code_units
            conv_factors.append(1.0)

        # Create label and unit label
        label = r'$' + fields[q]['label'] + r'\ (' + unit_label + r')$'
        q_labels.append(label)
    
    conv_factors = np.array(conv_factors)
    
    return q_array, conv_factors, q_labels, conv_l, unit_label_l

###################################################################################################

def plot1d(sim, q_plot = ['DN', 'VX', 'VY', 'PR'], 
        plot_unit_l = 'code', plot_unit_t = 'code', plot_unit_m = 'code',
        plot_type = 'line', true_solution_func = None, vminmax_func = None,
        radial_bins_per_cell = 4.0, invert_direction = False):
    """
    Plot fluid state along a 1D line
    
    Create a multi-panel plot of the fluid variables along a line through the domain. This 
    plotting routine is intended for pseudo-1D simulations, where the fluid state is uniform
    in the second dimension. The line is taken at the center of the domain in that dimension.
    The plot is created but not shown or saved to a file; these operations can be completed
    using the current matplotlib figure.
    
    Parameters
    ----------
    q_plot: array_like
        List of quantities to plot. Quantities are identified via the short strings given in the
        :data:`~ulula.plots.fields` dictionary.
    plot_unit_l: str
        Length unit to be plotted (see :data:`~ulula.utils.utils.units_l` for valid units). If other 
        than ``code``, ``plot_unit_t`` and ``plot_unit_m`` must also be changed from code units.
    plot_unit_t: str
        Time unit to be plotted (see :data:`~ulula.utils.utils.units_t` for valid units). If other 
        than ``code``, ``plot_unit_l`` and ``plot_unit_m`` must also be changed from code units.
    plot_unit_m: str
        Mass unit to be plotted (see :data:`~ulula.utils.utils.units_m` for valid units). If other 
        than ``code``, ``plot_unit_l`` and ``plot_unit_t`` must also be changed from code units.
    plot_type: str
        The type of cut through the domain that is plotted. Can be ``line`` (in which case the
        ``idir`` parameter specifies the dimension along which the plot is made), or ``radius``
        (which creates a radially averaged plot from the center).
    true_solution_func: function
        If not ``None``, the given function must return a 2D array with the true solution for
        the default fluid quantities and for a given input array of coordinates. This function
        is typically implemented within the problem setup (see :doc:`setups`).
    vminmax_func: function
        A function that returns two lists of minimum and maximum plot extents for the nq
        fluid variables, as well as whether to use a log scale. If ``None``, the limits are 
        chosen automatically.
    radial_bins_per_cell: float
        If ``plot_type == radius``, this parameter chooses how many radial bins per cell are
        plotted. The bins are averaged onto the radial annuli, so this number can be greater
        than one.
    invert_direction: bool
        By default, the plotted line is along the dimension (x or y) that has more cells, and along 
        x if they have the same number of cells. If ``True``, this parameter inverts the direction.
    """
    
    nq_plot = len(q_plot)
    q_array, conv_factors, q_labels, conv_l, unit_label_l = getPlotQuantities(sim, q_plot, 
                                        unit_l = plot_unit_l, unit_t = plot_unit_t, unit_m = plot_unit_m)
    
    if plot_type == 'line':
        
        xlabel = r'$x\ (' + unit_label_l + r')$'
        if sim.ny > sim.nx:
            idir = 1
        else:
            idir = 0
        if invert_direction:
            idir = int(not idir)
        if idir == 0:
            lo = sim.xlo
            hi = sim.xhi
            slc1d = slice(lo, hi + 1)
            slc2d = (slc1d, sim.ny // 2)
            x_plot = sim.x[slc1d]
        elif idir == 1:
            lo = sim.ylo
            hi = sim.yhi
            slc1d = slice(lo, hi + 1)
            slc2d = (sim.nx // 2, slc1d)
            x_plot = sim.y[slc1d]
        else:
            raise Exception('Unknown direction')
        xmin = x_plot[0]
        xmax = x_plot[-1]
        V_line = q_array[(slice(None), ) + slc2d]
        
    elif plot_type == 'radius':
        
        if (sim.nx % 2 != 0) or (sim.ny % 2 != 0):
            raise Exception('For plot type radius, both nx and ny must be multiples of two (found %d, %d)' \
                        % (sim.nx, sim.ny))
        xlabel = r'$r\ (' + unit_label_l + r')$'
        slc1d = slice(None)

        # The smaller side of the domain limits the radius to which we can plot
        xmin = 0.0
        nx_half = sim.nx // 2 + sim.nghost
        ny_half = sim.ny // 2 + sim.nghost
        x_half = sim.xmax * 0.5
        y_half = sim.ymax * 0.5
        if sim.nx >= sim.ny:
            xmax = 0.5 * (sim.ymax - sim.ymin)
            n_cells = sim.nx
        else:
            xmax = 0.5 * (sim.xmax - sim.xmin)
            n_cells = sim.ny
        n_cells_half = n_cells // 2
        
        # Radial bins
        n_r = int(n_cells_half * radial_bins_per_cell)
        bin_edges = np.linspace(0.0, xmax, n_r + 1)
        x_plot = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Compute weight in concentric circles
        slc_x = slice(nx_half - n_cells_half, nx_half + n_cells_half)
        slc_y = slice(ny_half - n_cells_half, ny_half + n_cells_half)
        cell_x, cell_y = sim.xyGrid()
        cell_x = cell_x[(slc_x, slc_y)]
        cell_y = cell_y[(slc_x, slc_y)]
        circle_weight = np.zeros((n_r, n_cells, n_cells), float)
        for i in range(n_r):
            circle_weight[i] = utils.circleSquareOverlap(x_half, y_half, bin_edges[i + 1], cell_x, cell_y, sim.dx)

        # Compute weight in bin annuli and normalize them 
        bin_weight = np.zeros((n_r, n_cells, n_cells), float)
        bin_weight[0] = circle_weight[0]
        for i in range(n_r - 1):
            bin_weight[i + 1] = circle_weight[i + 1] - circle_weight[i]
        bin_norm = np.sum(bin_weight, axis = (1, 2))

        # Create a square map that we use to measure the profile, then apply bin mask and sum
        V_2d = q_array[(slice(None), slc_x, slc_y)]
        V_line = np.sum(bin_weight[None, :, :, :] * V_2d[:, None, :, :], axis = (2, 3)) / bin_norm[None, :]

    else:
        raise Exception('Unknown plot type, %s.' % (plot_type))

    # Get true solution and min/max
    V_true = None
    if true_solution_func is not None:
        V_true = true_solution_func(sim, x_plot, q_plot)
        if (V_true is not None) and (V_true.shape[0] != nq_plot):
            raise Exception('Found %d quantities in true solution, expected %d (%s).' % (V_true.shape[0], nq_plot, str(q_plot)))

    ymin = None
    ymax = None
    if vminmax_func is not None:
        ymin, ymax, ylog = vminmax_func(q_plot)
        if (ymin is not None) and (len(ymin) != nq_plot):
            raise Exception('Found %d fields in lower limits, expected %d (%s).' % (len(ymin), nq_plot, str(q_plot)))
        if (ymax is not None) and (len(ymax) != nq_plot):
            raise Exception('Found %d fields in upper limits, expected %d (%s).' % (len(ymax), nq_plot, str(q_plot)))
        if (ylog is not None) and (len(ylog) != nq_plot):
            raise Exception('Found %d fields in log, expected %d (%s).' % (len(ylog), nq_plot, str(q_plot)))

    # Prepare figure
    panel_size = 3.0
    space = 0.3
    space_lb = 1.1
    fwidth  = space_lb + panel_size * nq_plot + space_lb * (nq_plot - 1) + space
    fheight = space_lb + panel_size + space
    fig = plt.figure(figsize = (fwidth, fheight))
    gs = gridspec.GridSpec(1, nq_plot)
    plt.subplots_adjust(left = space_lb / fwidth, right = 1.0 - space / fwidth,
                    bottom = space_lb / fheight, top = 1.0 - space / fheight, 
                    hspace = space_lb / panel_size, wspace = space_lb / panel_size)
    
    # Create panels
    panels = []
    for i in range(nq_plot):
        panels.append(fig.add_subplot(gs[i]))
        plt.xlim(xmin * conv_l, xmax * conv_l)
        if (ymin is not None) and (ymin[i] is not None) and (ymax is not None) and (ymax[i] is not None):
            if (ylog is not None) and ylog[i]:
                if ymin[i] <= 0.0 or ymax[i] <= 0.0:
                    raise Exception('Cannot create log plot for quantity %s with zero or negative limits (%.2e, %.2e).' \
                                % (q_plot[i], ymin[i], ymax[i]))
                plt.yscale('log')
            plt.ylim(ymin[i] * conv_factors[i], ymax[i] * conv_factors[i])
        plt.xlabel(xlabel)
        plt.ylabel(q_labels[i])
    
    # Plot fluid variables
    for i in range(nq_plot):
        plt.sca(panels[i])
        if V_true is not None:
            plt.plot(x_plot * conv_l, V_true[i, :] * conv_factors[i], 
                    ls = '-', color = 'deepskyblue', label = 'True solution')
        plt.plot(x_plot * conv_l, V_line[i, :], 
                    color = 'darkblue', label = 'Solution, t=%.2f' % (sim.t))

    # Finalize plot
    plt.sca(panels[0])
    plt.legend(loc = 1, labelspacing = 0.05)
    
    return

###################################################################################################

def plot2d(sim, q_plot = ['DN', 'VX', 'VY', 'PR'], 
        plot_unit_l = 'code', plot_unit_t = 'code', plot_unit_m = 'code',
        vminmax_func = None, cmap_func = None, panel_size = 3.0, plot_ghost_cells = False):
    """
    Plot fluid state in 2D
    
    Create a multi-panel plot of the fluid variables in 2D.
    The plot is created but not shown or saved to a file; these operations can be completed
    using the current matplotlib figure.
    
    Parameters
    ----------
    q_plot: array_like
        List of quantities to plot. Quantities are identified via the short strings given in the
        :data:`~ulula.plots.fields` dictionary.
    plot_unit_l: str
        Length unit to be plotted (see :data:`~ulula.utils.utils.units_l` for valid units). If other 
        than ``code``, ``plot_unit_t`` and ``plot_unit_m`` must also be changed from code units.
    plot_unit_t: str
        Time unit to be plotted (see :data:`~ulula.utils.utils.units_t` for valid units). If other 
        than ``code``, ``plot_unit_l`` and ``plot_unit_m`` must also be changed from code units.
    plot_unit_m: str
        Mass unit to be plotted (see :data:`~ulula.utils.utils.units_m` for valid units). If other 
        than ``code``, ``plot_unit_l`` and ``plot_unit_t`` must also be changed from code units.
    vminmax_func: function
        A function that returns two lists of minimum and maximum plot extents for the nq
        fluid variables, as well as whether to use a log scale. If ``None``, the limits are 
        chosen automatically.
    cmap_func: function
        A function that returns a list of size nq with colormap objects to be used when 
        plotting the fluid variables. If ``None``, the default colormap is used for all
        fluid variables.
    panel_size: float
        Size of each plotted panel in inches
    plot_ghost_cells: bool
        If ``True``, ghost cells are plotted and separated from the physical domain by a gray
        frame. This option is useful for debugging.
    """

    # Constants
    space = 0.15
    space_lb = 0.8
    cbar_width = 0.2
    
    # Compute quantities
    nq_plot = len(q_plot)
    q_array, conv_factors, q_labels, conv_l, unit_label_l = getPlotQuantities(sim, q_plot, 
                                    unit_l = plot_unit_l, unit_t = plot_unit_t, unit_m = plot_unit_m)

    # Get x-extent
    if plot_ghost_cells:
        xlo = 0
        xhi = sim.nx + 2 * sim.nghost - 1
        ylo = 0
        yhi = sim.ny + 2 * sim.nghost - 1
        
        xmin = sim.x[0] - 0.5 * sim.dx
        xmax = sim.x[-1] + 0.5 * sim.dx
        ymin = sim.y[0] - 0.5 * sim.dx
        ymax = sim.y[-1] + 0.5 * sim.dx
    else:
        xlo = sim.xlo
        xhi = sim.xhi
        ylo = sim.ylo
        yhi = sim.yhi
        
        xmin = sim.xmin
        xmax = sim.xmax
        ymin = sim.ymin
        ymax = sim.ymax

    # Apply units
    xmin *= conv_l
    xmax *= conv_l
    ymin *= conv_l
    ymax *= conv_l
    
    slc_x = slice(xlo, xhi + 1)
    slc_y = slice(ylo, yhi + 1)
    xext = xmax - xmin
    yext = ymax - ymin
    
    # Prepare figure; take the larger dimension and assign that the panel size; the smaller
    # dimension follows from that.
    if xext >= yext:
        panel_w = panel_size
        panel_h = yext / xext * panel_w
    else:
        panel_h = panel_size
        panel_w = xext / yext * panel_h
    
    fwidth  = space_lb + (panel_w + space) * nq_plot
    fheight = space_lb + panel_h + space + cbar_width + space_lb
    
    fig = plt.figure(figsize = (fwidth, fheight))
    gs = gridspec.GridSpec(3, nq_plot, height_ratios = [space_lb * 0.8, cbar_width, panel_h])
    plt.subplots_adjust(left = space_lb / fwidth, right = 1.0 - space / fwidth,
                    bottom = space_lb / fheight, top = 1.0 - space / fheight, 
                    hspace = space / fheight, wspace = space / panel_w)
    
    # Create panels
    panels = []
    for i in range(nq_plot):
        panels.append([])
        for j in range(3):
            panels[i].append(fig.add_subplot(gs[j, i]))
            
            if j == 0:
                plt.axis('off')
            elif j == 1:
                pass
            else:
                plt.xlim(xmin, xmax)
                plt.ylim(ymin, ymax)
                plt.xlabel(r'$x\ (' + unit_label_l + r')$')
                if i == 0:
                    plt.ylabel(r'$y\ (' + unit_label_l + r')$')
                else:
                    plt.gca().set_yticklabels([])
    
    # Check for plot limits and colormaps specific to the setup
    vmin = None
    vmax = None
    if vminmax_func is not None:
        vmin, vmax, vlog = vminmax_func(q_plot)
        if (vmin is not None) and (len(vmin) != nq_plot):
            raise Exception('Found %d fields in lower limits, expected %d (%s).' % (len(vmin), nq_plot, str(q_plot)))
        if (vmax is not None) and (len(vmax) != nq_plot):
            raise Exception('Found %d fields in upper limits, expected %d (%s).' % (len(vmax), nq_plot, str(q_plot)))
        if (vlog is not None) and (len(vlog) != nq_plot):
            raise Exception('Found %d fields in log, expected %d (%s).' % (len(vlog), nq_plot, str(q_plot)))
        
    cmaps = None
    if cmap_func is not None:
        cmaps = cmap_func(q_plot)
        if (cmaps is not None) and (len(cmaps) != nq_plot):
            raise Exception('Found %d fields in colormaps, expected %d (%s).' % (len(cmaps), nq_plot, str(q_plot)))
    
    # Plot fluid variables
    for i in range(nq_plot):
        plt.sca(panels[i][2])
        data = q_array[i, slc_x, slc_y]
        data = data.T[::-1, :]
        
        if (vmin is None) or (vmin[i] is None):
            vmin_ = np.min(data)
        else:
            vmin_ = vmin[i] * conv_factors[i]
        if (vmax is None) or (vmax[i] is None):
            vmax_ = np.max(data)
        else:
            vmax_ = vmax[i] * conv_factors[i]
        if (vlog is not None) and (vlog[i] is not None):
            log_ = vlog[i]
        else:
            log_ = False
        if (cmaps is None) or (cmaps[i] is None):
            cmap = plt.get_cmap(fields[q_plot[i]]['cmap'])
        else:
            cmap = cmaps[i]
            
        # Check that limits and log make sense
        if log_:
            if (vmin_ <= 0.0) or (vmax_ <= 0.0):
                raise Exception('Cannot use negative limits with in log space (quantity %s, limits %.2e, %.2e).' \
                            % (q_plot[i], vmin_, vmax_))
            vmin_ = np.log10(vmin_)
            vmax_ = np.log10(vmax_)
            if np.min(data) <= 0.0:
                raise Exception('Cannot plot zero or negative data in field %s on log scale.' % (q_plot[i]))
            data = np.log10(data)
            label_use = r'$\log_{10}$' + q_labels[i]
        else:
            label_use = q_labels[i]
            
        norm = mpl.colors.Normalize(vmin = vmin_, vmax = vmax_)
        plt.imshow(data, extent = [xmin, xmax, ymin, ymax], interpolation = 'nearest', 
                cmap = cmap, norm = norm, aspect = 'equal')

        ax = panels[i][1]
        plt.sca(ax)
        cb = mpl.colorbar.ColorbarBase(ax, orientation = 'horizontal', cmap = cmap, norm = norm)
        cb.set_label(label_use, rotation = 0, labelpad = 8)
        cb.ax.xaxis.set_ticks_position('top')
        cb.ax.xaxis.set_label_position('top')
        cb.ax.xaxis.set_tick_params(pad = 5)
        
        # Plot frame around domain if plotting ghost cells
        if plot_ghost_cells:
            plt.sca(panels[i][2])
            plt.plot([sim.xmin, sim.xmax, sim.xmax, sim.xmin, sim.xmin], 
                    [sim.ymin, sim.ymin, sim.ymax, sim.ymax, sim.ymin], '-', color = 'gray')
    
    return

###################################################################################################
