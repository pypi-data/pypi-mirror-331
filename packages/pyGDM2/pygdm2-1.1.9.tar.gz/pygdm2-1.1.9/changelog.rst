Changelog
*********

(unreleased)
=====================



[v1.1.9] - 2025-03-05
=======================
fixes
--------------
- multipole expansion: nearfield propagation of multipoles - fixed bug if multiple magnetic quardupoles



[v1.1.8] - 2024-10-17
=======================
fixes
--------------
- sign error in asymptotic surface Green's tensor below the interface
- contour plot: improved stability
- internal plot improvements
- fix in multipole expansion of the extinction



[v1.1.7] - 2024-09-24
=======================
fixes
--------------
- image to struct: fixed PIL deprecations
- some improvements in exception handling and fixes in doc



[v1.1.6] - 2024-04-30
=======================
added
--------------
- Rewrite of `visu.structure_contour`: More robust and nicer plotting, with smoothing. Based on contribution by Simon Garrigou (thanks!).

fixes
--------------
- Bugfix in extract effective polarizability (via dipole illuminations)
- Bugfix in `tools.adapt_map_to_structure_mesh`



[v1.1.5.1] - 2024-03-05
=======================
fixes
--------------
- `linear.farfield` and `multipole.farfield`: Fixed exception handling in calculation of far-field patterns 



[v1.1.5] - 2024-01-25
=======================
added
--------------
- `multipole`: extract effective point polarizabilities: Save addition info (original mesh, enclosing radius, simulation object now optional)



[v1.1.4.1] - 2023-10-05
=======================
added
--------------
- new geometry model: `structures.ellipse`

fixes
--------------
- fixed error in calculation of the magnetic nearfield under vector-beam illuminations



[v1.1.4] - 2023-06-30
=====================
added
--------------
- `multipole`: several functions and tools for more flexible multiple-multipole calculations in near- and far-field

fixes
--------------
- fixed compatibility with numpy after recent numpy deprecations



[v1.1.3.2] - 2022-07-07
=======================
fixes
--------------
- fixed sign error in `core.decay_rate` for magnetic LDOS (bug was introduced in v1.1.3.1)
- fixed rare issues with save/load and hdf5 together with emtpy simulations



[v1.1.3.1] - 2022-04-28
=======================
changes
--------------
- some minor default parameter changes in `multipole`

fixes
--------------
- critical fix in `core.decay_rate`: correct off-diagonal elements in field susceptibilities for LDOS and CDOS



[v1.1.3] - 2022-04-26
=====================
added
--------------
- `multipole`: several functions and tools for generalized polarizabilities
- `multipole`: extraction of effective electric and magnetic dipolar polarizabilties
- module `propagators_periodic`: working experimental version of periodic Green's tensors
- focused vectorbeams now support transmission through a dielectric interface and arbitrary polarizations

changes
--------------
- `fields` is now a subpackage
- `propagators` is now a subpackage containing the different sets of Green's dyads
- `materials.fromFile`: can be used alternatively with numpy arrays as input
- `tools.calculate_spectra` now supports optional parallelization via multiprocessing

fixes
--------------
- `linear.farfield`: fixed missing cast to integer, causing errors in some cases
- `core.decay_rate`: now handles correctly input types tuple / list / np.ndarrays



[v1.1.2] - 2021-12-10
=====================
added
--------------
- new `linear.poynting`: calculate time average Poynting vector at any location for incident, scattered or total field
- `materials.germanium`: added hardcoded Germanium refractive index
- new module `multipole`: *exact multipole decomposition*, based on Alaee et al Opt. Comm. 407, 17 (2018). Includes electric and magnetic dipoles and quadrupoles. 
- `multipole.extinct`: decomposition of the extinction cross section into multipoles
- `multipole.scs`: decomposition of the scattering cross section into multipoles

changes
--------------
- `structures.center_struct`: added optional definition of the centering axes (one or several)

fixes
--------------
- `core.scatter`: free memory prior next wavelength. Avoids out-of-memory-errors in some cases.
- `fields.plane_wave`: fixed an error in the relative field amplitudes ratio E0/H0 for certain configurations under p-polarization



[v1.1.1.1] - 2021-06-04
=======================

fixes
--------------
- `linear.extinct`: fixed wrong factor in non-vacuum environmets
- `linear.nearfield`: fixed the case of calculating only the incident field E0 / B0



[v1.1.1] - 2021-05-10
=====================
added
--------------
- *experimental* New illuminations. Special focused beams: Hermite-Gauss modes, radially polarized and azimuthally polarized doughnut modes, all supporting tight focus (contributed by A. Arbouet)
- added optional normalization to peak incident field intensity inside nanostructre in `linear.extinct` and  `linear.farfield` for cross-section calculations

fixes
--------------
- `fields.efield`: internally a copy of `kwargs` is now used to avoid unexpected modification of the dictionary
- code optimization in `linear.farfield`: the incident field is now only evaluated if it is actually used (contributed by A. Arbouet)
- code optimization in `linear.nearfield`: omit unnecessary Green's tensors calculation for positions inside structure
- fix in `structures.image_to_struct` with hexagonal mesh



[v1.1] - 2021-04-07
===================
The pure-python API replaces the former fortran API (former modules `core_py`, `fields_py`, `linear_py` replace the main modules). 
The high-level syntax remains compatible, but the internal API has changed. 
The former fortran based implementation is not included in pyGDM anymore by default. It can still be compiled manually from sources (--with-fortran option). It is then accessible via `pyGDM2.f_api`.

breaking
--------------
- new API is internally not compatible with the former fortran-based API
- `fields` generators use new argument convention
- `structures.struct` and `core.simulation` use new description of the environment based on the `propagators.DyadsBaseClass` reference class
- behavior of `tools.generate_NF_map_xxx` changed! They now return list of coordinates.

added
--------------
- consistent class attributes like `copy`, info-printing etc. for 'struct', 'efield', 'dyads' and 'simulation'
- combine structures and simulations by python addition: combined_struct = struct1 + struct2, combined_sim = sim1 + sim2
- shift structures by python addition: shifted_struct = struct1 + [100, -50, 0]
- experimental support for arbitrary wavefronts in "fields.gaussian"
- documentation: several examples
- calculation of field gradients and optical forces (contribution C. Majorel)
- support of callback functions
- full support of pyGDM-UI GUI (still experimental)

changes
--------------
- full implementation of the main API in pure python
- adapted tutorials and examples to new API

fixes
--------------
- code cleaning in the Dyads classes
- added available memory check for CUDA-solver. If not enough GPU-RAM, fall back to CPU solver
- Sign error in "linear.optical_chirality"
- `linear.nearfield`: order of elements in 'which_fields' is now correctly treated
- several bugfixes in new code: automatic mesh detection optimized, structure-contour plots improved, fixes in structure-consistency check
- visu: automatically choose closest available slice level instead of rising an exception



[v1.0.12] - 2020-11-30
======================
experimental
--------------
- new module `core_py`: experimental python implementation, will replace old fortran dependencies in the future. All development will go into the python API, new functions will only be added via the new API.
- new implementation `core_py.scatter` supports calculation of internal magnetic fields (contributed by C. Majorel)
- new implementation `core_py.decay_rate`, much faster, optimized numba-code, can calculate both E and H LDOS inside structures. *breaking!!* uses a new API!
- new `core_py.simulation.dyads` attribute: the python implementation is based on a new API for the flexible exchange of the Green's Dyads. This new attribute contains also all information on the environment
- default Greens-tensors now in the `propagators.G_123_quasistatic` class. This includes also the environment configuration: n1, n2, n3, spacing. The indices can be instances of materials-classes (e.g. for a dispersive substrate).
- structure can be placed in any of the three layers now ('1', '2' or '3'). But it must be still fully lying in one of the layers.
- new `propagators_2D` module for simulations with set of 2D Greens Dyads (infinitely long nanowires). Also supports 1-2-3 layered (and dispersive) system in a quasistatic approximation. Only compatible with the new pure-python API. 
- new class `structures.struct_py`: for pure-python interface, contains only structure-related information
- new module `fields_py`: pure-python implementation of all incident field related code *breaking!!* new API!
- new module `electron.py` and incident field `field_py.fast_electron`, for cathodoluminescence (CL) and electron energy loss (EELS) simulations. Only compatible with the new pure-python API. Contributed by Arnaud Arbouet (CEMES-CNRS).

added
--------------
- dispersion in the substrate / environment / cladding medium possible: the environment ref.index parameters `n1`, `n2`, `n3` can now be instances of material classes
- added tool to split the geometry of a simulation, returning two simulation objects
- added a `core.simulation.scatter` attribute to the simulation class to directly launch the scatter-simulation.
- new material `materials.sio2`, contributed by Clément Majorel

fixes
--------------
- "evanescent plane wave" field generator now works for bottom- and top-incident angles. New python implementation contributed by C. Majorel.
- another bugfix in `fields.evanescent_planewave` for environments n1 or n3 other than vacuum (!= 1)
- fixed `linear.nearfield` and `linear_py.nearfield`: total and scattered field inside source zone
- fixes in exception handling in `linear.farfield`
- fixed incorrect sign of magnetic field in new `linear_py.nearfield`
- fixed non-cubic mesh representation problems in `visu.structure_contour`

breaking
--------------
- functions in `core_py` and `linear_py` now require instances of `core_py.simulation`, `structures.struct_py` and fields must be using the new fields-API as defined in `fields_py`
- new implementation of `core.decay_rate` has a different, hopefully easier API
- structure generators yield geometries positioned at H=step/2. Before, formerly this was automatically done in the constructor of `structures.struct`, so in normal use-cases this change should not be an issue.
- removed the inefficient/redundant solvers "superlu", "pinv2" and "skcuda" to clean the code.
- removed deprecated `EO1` submodule, which was based on the no longer maintained `pygmo1` package



[v1.0.11.1] - 2020-05-05
========================
fixes
--------------
- fixed pypi multi-dist source package



[v1.0.11] - 2020-02-25
======================
breaking
--------------
- internal API changes in `core`: re-structured `scatter` and `get_generalized_propagator`. The latter now takes a `sim` instance as input. The order of kwargs was changed.

added
--------------
- added a geometry consistency check to structure class
- new module `linear_py` with experimental pure python implementations of all linear functions
- optional radiative correction term in "linear_py.extinct" (can improve absorption section with large stepsizes)
- `visu`: 2D plotting functions try to determine the best 2D projection automatically
- started writing unit tests
- callback function support for `core.scatter` 

changes
--------------
- conversion to pure python of some helper functions
- some internal modifications for pygdmUI GUI support

fixes
--------------
- fixed geometry consistency-test routine for multi-material structures
- fixes in autoscaling in `visu.structure` (TODO: adapt to screen dpi)
- fixed bug in "linear.farfield" in cases when n2>n1 ("environment" optically denser than "substrate")
- **potentially breaking!!**: fixed several structures, where "hex" meshing gave a wrong height. *Attention*, following structure generators may now produce different heights: `lshape_rect`, `lshape_rect_nonsym`, `lshape_round`, `split_ring`, `rect_split_ring`
- some code cleaning
- minor fixes in several visualization tools



[v1.0.10.1] - 2019-10-08
========================
added
--------------
- `materials.hyperdopedFromFile`: materials class, which adds doping to any tabulated dielectric permittivity (contributed by C. Majorel)

fixes
--------------
- fixed bug in "linear.farfield", causing zero scattering at angles teta > 3pi / 2



[v1.0.10] - 2019-10-02
======================
added
--------------
- `linear.optical_chirality`: chirality of the electromagnetic field (experimental feature)
- new structure generator `polygon`
- `tools.combine_simulations`: tool to combine the structures of several simulations into a single simulation. Combining simulations with calculated fields, this also allows to analyze how structures behave if optical interactions are artificially deactivated.
- added support for "cupy" GPU solver (req. version 7+) as alternative to "pycuda"
- added experimental pure-python implementation of propagators and coupling matrix initialization routines based on "numba" (by default pygdm is still using the former fortran implementation)
- added experimental support for tensorial material permittivity

fixes
--------------
- critical fix in "linear.extinct": Works correctly now for environments n2!=1
- corrected phase of B-field in field generators "planewave" and "gaussian"
- fieldindex-search: works now with strings as fieldgenerator kwargs
- added exception handling to "linear.farfield" for simulation configurations where the underlying approximations don't apply



[v1.0.9] - 2019-08-22
=====================
no more compiled binaries for python 2.7 (compilation from source still possible)

fixes
--------------
- critical fix in linear.farfield: works correctly now also for non-vacuum environment above the substrate (refractive index n2 != 1)



[v1.0.8] - 2019-06-07
=====================
added
--------------
- multipole decomposition (dipole and quadrupole moments)
- elliptic polarization in field generators "planewave", "focused" and "gaussian"
- new materials: *hyperdopedSilicon* and *hyperdopedConstantDielectric* (contributed by C. Majorel)
- extended capabilities for "visu3d.animate_vectorfield" and according documentation
- zero-field generator

fixes
--------------
- linear.farfield: scattering into a substrate now correctly calculated (contributed by C. Majorel)
- python3 compatibility: fixed structure generator problem with hexagonal meshing and some float parameters. Also fixed the python 3.X compatibility of the examplescripts.
- fixed a bug in silver dispersion
- numerous small fixes and docstring improvements



[v1.0.7] - 2018-11-20
=====================
added
--------------
- experimental CUDA support for matrix inversion on GPU (method "cuda")
- structure generators:
    - "prism" now supports truncated edges
    - "spheroid"

fixes
--------------
- MAJOR: fix absolute import error in "visu3d"module, which was broken in former version
- minor fix in struct class, treats lists of wavelengths correctly now (was not affecting pyGDM itself. Failed if a `struct` instance was externally used with a list of wavelengths)



[v1.0.6] - 2018-10-31
=====================
added
--------------
- compatibility with python3 (compatible with python 2 and 3 now)
- default inversion method is now in-place LU decomposition: reduces memory requirement by ~40%
- added some tools to simplify intensity calculation

fixes
--------------
- fix in visu.animate: Works now glitch-less with any user-defined framerate
- minor fix: all classes now initialize with single precision by default. 



[v1.0.5] - 2018-07-9
====================
fixes
--------------
- critical fix in hdf5 saving / loading. hdf5-data was corrupted during saving/reloading. Works now.

minor
--------------
- by default, multithreading disabled in MPI-version of "scatter". Using SLURM, MPI and pathos seems to conflict which results in major performance drop



[v1.0.4] - 2018-06-07
=====================
added
--------------
- multi-threading support via "thanos" in generalized propagator operations. 
  This drastically increases the speed of raster-scan simulations on multi-core systems.
- hdf5 support for saving/loading simulations
    - doubles the speed for writing, triples speed for reading
    - by default, using "blosc" compression, reduces the filesize by ~ 50%
- hexagonal meshing support in "image_to_struct"
- support for scipy < V0.17 in "decay"



[v1.0.3] - 2018-04-06
=====================
added
--------------
- intallation instructions for MacOSX



[v1.0.2] - 2018-03-29
=====================
added
--------------
- "visu.structure" does automatic multi-structure plots
- compile option for compilation without openmp
- several structure models
- hardcoded silver dielectric function

fixes
--------------
- in "visu.vectorfield_color", fixed an error in the calculation of the field intensity



[v1.0.1] - 2018-02-13
=====================
fixes
--------------
- fixes in "setup.py" script
