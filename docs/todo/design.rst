

# engine has timer

What actors do we support
-------------------------
* ConnectedSlices
* Surface
* ODFSlicer
* Network
* Dandelion
* InteractiveCurves (for Trackfiles)

* Video
* Audio


What are potential data sources?
--------------------------------

I will refer to basic building blocks such as voxel, pixel, nodes, vertices, lines as elements.
And to links, streamlines (=sequence of lines) as connecting elements.
 
(I'd like to think of both these elements as spatio-temporal atoms!)

* 5D homogenous arrays
** 1./2./3. dim : space; the 3d location of the elements
** 4. dim : time
** 5. dim : can be different things : channels / individuals / conditions

* 3D surfaces
** a sequence of vertex elements
** a sequence of faces (triangles, quads)

* 3D graphs
** a set of nodes
** a set of links

* Streamlines
** a set of streamlines (=polygons), where each streamline consists of a sequence of lines


---

Attributes that elements and connecting elements can have:
* color (e.g. defined directly or via a colormap)
* scale (i.e. the extend in the 3 spatial, and 1 temporal dimension)

Numpy array axes need to have more attributes:
* What is its name?
* Indices that represent what is loaded in memory (RAM or GPU)? (i.e. which dataset is currently worked on)
* Indices that represent what is cached? 
* What is visible?
* What is selected? (see picking, see spatial data structures)

Interactions
* Select an element or a connecting element
* Change affine parameters: translation (in 3d or 4d!), scale, rotate, shear, ...


---

Time Dimension (4th)
--------------------

Animation Toolbar:
<< < Block Play > >> Circle

fast back, 1 step back, stop, play, 1 step forward, fast forward, play in loop

Comments:
* frame rate vs. sampling rate. Maybe have a speed up range
* real milisecond timestamps per frame?
* What to do with inhomogenous time frame distributions?
* Idea: Represent only the "logcial" point in the data, detached from actual memory and display management.

Questions:
* What can change in the time evolution?
** geometry : location in 3d, topology
** attributes : colors, opacity, size (?)

---

Comments:
* We might want to have "streamable" sources. With this I mean e.g. memory mapped sources
  (The data resides on harddisk and is retrieved upon request)
* What could we do about missing data points? E.g. missing time frames etc.
* Related to the 5. dim, channels could be regardes as attributes,
* 5D arrays might be isotropic or anisotropic. Can this be accounted for in the voxel element scaling in the 3 spatial dimensions?
  Idea: Scale for dim 1-3 is spatial, scale for dim 4 is sampling interval duration, for dim 5 it might be a different semantic concept
  (nominal), e.g. wavelength band, particular individual or experimental condition
* Idea: Raycast in 3D and change the depth to select a 3D location, instead of selecting on orthoslices.
* Do we need a SceneGraph? If so, should we make it as tree or really as graph? Does it represent "change in parameters" (e.g. appereance)
  or "transformations" ?
* Using 2D sprites to create the impression of 3D, or use truly 3D. Scaling up?
* Support for multi-touch screens and audio/video/camera is also important so we can create immersive environments.
* Multithreading and scheduling is also something important. We need very fast threads.
http://stackoverflow.com/questions/1961203/python-separating-the-gui-process-from-the-core-logic-process
http://stackoverflow.com/questions/1182315/python-multicore-processing
* Idea: zoom in and out of spatio-temporal patterns, spatio-temporal dynamic filter

---
