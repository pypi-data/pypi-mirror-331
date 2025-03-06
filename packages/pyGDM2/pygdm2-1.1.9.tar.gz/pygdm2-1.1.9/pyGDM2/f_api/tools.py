# encoding: utf-8
#
#Copyright (C) 2017-2022, P. R. Wiecha
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
#
"""
Collection of tools only for former API
"""

from __future__ import print_function
from __future__ import absolute_import

import itertools
import warnings
import cmath

import numpy as np








def evaluate_incident_field(field_generator, wavelength, kwargs, r_probe, 
                            n1=1.0,n2=1.0,n3=None, spacing=5000.0):
    """Evaluate an incident field generator
    
    Calculate the field defined by a field_generator function for a given set
    of coordinates.
      
    Parameters
    ----------
    field_generator : `callable`
        field generator function. Mandatory arguments are 
         - `struct` (instance of :class:`.structures.struct`)
         - `wavelength` (list of wavelengths)
    
    wavelength : float
        wavelength in nm
    
    kwargs : dict
        optional kwargs for the `field_generator` functions (see also 
        :class:`.fields.efield`).
         
    r_probe : tuple (x,y,z) or list of 3-lists/-tuples
        (list of) coordinate(s) to evaluate nearfield on. 
        Format: tuple (x,y,z) or list of 3 lists: [Xmap, Ymap, Zmap] 
        (the latter can be generated e.g. using :func:`.tools.generate_NF_map`)
    
    n1,n2,n3 : complex, default: 1.0, 1.0, None
        indices of 3 layered media. if n3==None: n3=n2.
        
    spacing : float, default: 5000
        distance between substrate and cladding (=thickness of layer "n2")
    
    Returns
    -------
    field_list : list of tuples
        field at coordinates as list of tuples (x,y,z, Ex,Ey,Ez)
    
    """
    warnings.warn("This function is deprecated and only compatible with pyGDM 1.0.x field-generators.")
    
    
    from pyGDM2.tools import get_step_from_geometry
    from pyGDM2 import materials
    from pyGDM2.f_api import structures
    
    ## ---------- Setup dummy-structure for fundamental field-calculation
    r_probe = np.array(r_probe)
    if len(r_probe.shape)==1:
        r_probe = np.array([r_probe])
    if r_probe.shape[0] == 3 and r_probe.shape[1] != 3:
        r_probe = r_probe.T
    if r_probe.shape[-1] != 3:
        raise ValueError("'r_probe': Wrong shape or wrong number of coordinates.")
    
    ## dummy parameters
    material = materials.dummy(1.0)
    geometry = r_probe
    step = get_step_from_geometry(geometry)
    
    struct = structures.struct(
                    step, geometry, material, 
                    n1,n2, 1.0, n3=n3, spacing=spacing, 
                    auto_shift_structure=False, check_geometry_consistency=False
                    )
    struct.setDtype(np.float32, np.complex64)
    struct.geometry = r_probe
    struct.setWavelength(wavelength)
    
    E = field_generator(struct, wavelength, **kwargs)
    NF = np.concatenate([struct.geometry, E], axis=1)
    
    return NF
    