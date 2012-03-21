Possible use cases for scientific 3d visualization, in particular for the neurosciences.

* Fiji / TrackEM2 3D/5D Image Viewer with use cases
* change subject/modality/add/remove, needs registration
* Allen Brain Atlas
* Connectomes from Electrom Microscopy
* Tracking data of cell migration
* Tracking data of neuronal processes
* Whole Brain Catalog

* Display a movie simultaneously with dynamic data, e.g. brain activation.
** For optical imaging with visual stimuli
** Of course fMRI/MEG/EEG with visual stimuli

* Play a sound simultanesouly with dynamic data
** Of course for auditory stimuli

* In general, seeing structural data together with dynamic data
** Tracs with dynamic data (from fMRI/EEG/MEG) overlay on/as (transparent) surfaces or volume renderings


---

different data types we would need for a neuroscience visualization engine. Please update:
* surfaces: (triangle)meshes
* volumes: cubes, volume rendering
* tracks: polygons
* diffusion: odf, tensor
* networks: points, spheres, polygons, tubes, arrows, (bending edges)
* labels      
* 2d images,  tile them in different ways, compress them in memory, or show them in many different resolutions. 
* plots
* animation
* math fonts 
* direct interaction - e.g. picking individual tracks or other objects in multiple datasets

 And perhaps also say that we will be able to see more datasets than before and load them faster.  
 
 ----
 
 * Use Fos as a "remote" service
 
 A future area of interest for Kitware is support for distance visualization. Being able to view
 the results of a simulation without having to move the data off the supercomputing site is becoming
 more necessary as datasets grow in size. Along those same lines is the concept of collaborative visualization,
 enabling multiple researchers at different sites to share results and look at the data together. A lot of this
 will be enabled by Web-based interfaces, which are slowly edging out the traditional desktop GUI. "The idea is
 to share data and visualization of data as a larger community," explains Geveci. "Enabling sharing of data and
 results through distance visualization and collaboration is very important to us and I think is going to be
 important to the community at large."


----

* model
1. take a neuron skeleton
2. transform to V,E, and P
3. find graph laplacian and compute eigendecomposition
4. apply the coordinate signal to a subspace
5. see what is coming out
* efficiently convert mesh to a graph
* highlight streamlines "active" in time based on connecting roi activation

