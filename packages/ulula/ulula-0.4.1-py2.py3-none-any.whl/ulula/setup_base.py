###################################################################################################
#
# This file is part of the ULULA code.
#
# (c) Benedikt Diemer, University of Maryland
#
###################################################################################################

import six
import abc

###################################################################################################

@six.add_metaclass(abc.ABCMeta)
class Setup():
    """
    General setup class
    
    This abstract container must be partially overwritten by child classes, but also contains 
    defaults for a number of standard routines.
    """
    
    def __init__(self):
        
        self.gravity = False
        
        return

    # ---------------------------------------------------------------------------------------------

    @abc.abstractmethod
    def shortName(self):
        """
        Short name for the problem (to be used in output filenames)
        """
        
        return

    # ---------------------------------------------------------------------------------------------
    
    def initialConditions(self, sim, nx):
        """
        Wrapper function to set initial data
        
        This function calls the problem-specific setup, which is assumed to set the primitive 
        variables. Those are also converted to conserved variables.
        
        Parameters
        ----------
        sim: Simulation
            Simulation object in which the ICs are to be set
        nx: int
            Number of cells in the x-direction
        """
        
        # Call the user-defined function to set the initial conditions
        self.setInitialData(sim, nx)
        
        # We need to set the gravitational fields before any prim-cons conversions
        sim.setGravityPotentials()
        
        # Now create the correct conserved initial conditions and BCs
        sim.primitiveToConserved(sim.V, sim.U)
        sim.enforceBoundaryConditions()
        
        return

    # ---------------------------------------------------------------------------------------------

    @abc.abstractmethod
    def setInitialData(self, sim, nx):
        """
        Set the initial conditions (must be overwritten)

        This function 

        Parameters
        ----------
        sim: Simulation
            Simulation object in which the ICs are to be set
        nx: int
            Number of cells in the x-direction
        """
        
        return

    # ---------------------------------------------------------------------------------------------

    def trueSolution(self, sim, x, q_plot):
        """
        Return a true solution for this setup
        
        This function can be passed to the Ulula 1D plotting routine 
        :func:`~ulula.plots.plot1d`. It must return a 2D array, with the solution in 
        primitive variables for a given input vector of coordinates. The solution must be returned in
        code units.

        Parameters
        ----------
        sim: Simulation
            Simulation object
        x: array_like
            The coordinates where the true solution is to be computed.
        q_plot: array_like
            List of quantities for which to return the true solution. Quantities are identified via 
            the short strings given in the :data:`~ulula.plots.fields` dictionary.

        Returns
        -------
        solution: array_like
            A 2D array with dimensions (len(q_plot), len(x)) in code units.
        """
        
        return

    # ---------------------------------------------------------------------------------------------

    def plotLimits(self, q_plot):
        """
        Return min/max limits for plotted quantities
        
        This function can be passed to the Ulula plotting routines. By default, no limits are 
        returned, which means the plotting functions automatically select limits. The limits must
        be in code units.

        Parameters
        ----------
        q_plot: array_like
            List of quantities for which to return the plot limits. Quantities are identified via 
            the short strings given in the :data:`~ulula.plots.fields` dictionary.

        Returns
        -------
        limits_lower: array_like
            List of lower limits for the given plot quantities. If ``None``, a limit is chosen 
            automatically. Individual items can also be ``None``.
        limits_upper: array_like
            List of upper limits for the given plot quantities. If ``None``, a limit is chosen 
            automatically. Individual items can also be ``None``.
        log: array_like
            List of True/False that determine whether to plot in log space. If ``None``, all 
            quantities are plotted in linear space. If log is chosen, the limits must be positive.
        """
        
        return None, None, None

    # ---------------------------------------------------------------------------------------------

    def plotColorMaps(self, q_plot):
        """
        Return colormaps for plotted quantities
        
        This function can be passed to the Ulula plotting routines. By default, velocities are 
        plotted with a divergent colormap, whereas density and pressure are plotted with a 
        perceptually uniform colormap.

        Parameters
        ----------
        q_plot: array_like
            List of quantities for which to return the colormaps. Quantities are identified via 
            the short strings given in the :data:`~ulula.plots.fields` dictionary.

        Returns
        -------
        cmaps: array_like
            List of colormaps for the given quantities. If ``None``, a colormap is chosen 
            automatically. Individual items can also be ``None``.
        """
        
        return None

###################################################################################################
