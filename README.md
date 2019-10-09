# SpaceClaim_scripts
 Assitant script for accelerating the modeling
 *Noted*: This scripts are in the test phase.
 
 *To use the script, load it in SpaceClaim. For the usage of the script, by default it is: select one solid, and run the script for this solid. For more details please check the first block of the script if available.*
 
 ## Piping decomposition script (Split_pipes.scscript)

Often neutronics model has to include many pipes inside the model. The pipes consist of many elbow formed by torus surface, which causes difficulty for the modeling. A reason is that the torus surfaces which are not parallel to the X/Y/Z coordinate with their axis are not supported in the MCNP code. In order to handle this issue, a SpaceClaim plugin has been developed for cutting and simplify the pipes. 
The plugin work in the following flows:
•	All the curve of pipe has been check, and the circular curve is put into a list;
•	Removing the circular curve when it has the same origin (center point) with another curve in the list;
•	Uses the circular curve only when they are used for a cylindrical or torus surface, otherwise they are consider the interface curve of the pipe;
•	Create a plane on the circular curve, and use this plan to cut the pipe;
•	Recursively cur the resultant parts, until they cannot be cut into two or more parts

## Elbow simplificatioin script (Pipe_torus_to_cylinder.scscript)

This plugin is developed for simplified the elbow to cylindrical elbow. This plugin can put together with the decomposition plugin in the future development.The workflow of the plugin is descript as follow:
•	Check if the elbow is larger than 90°, and split it by half, if yes, create the mid-plane of two sketching face, and split the solid using this plane;
•	Get the plane of the two sketching face, and calculate the mid-plane again of these two sketching face.
•	Pull the sketching face up to the mid-plane, and form a cylindrical elbow. 

## Model export script (Model_group_save.scscript)

After processing and decomposing the model in SpaceClaim, next steps is to export the model to STEP format files. Because the material information in the model cannot be persisted in the STEP format, therefore the materials information assigned in the SpaceClaim platform cannot be convey directly to McCad. The common approach is to separate the model into several groups based on their material properties, and  save the solid in one or more files in the same folder with the same material. It needs lot of human effort in saving those file individually, and at the same time keeping the component information and the material information, i.e. the rename the exported files with the file name associate with the component information (i.e. blanket, vacuum vessel). Here, a solution found to provide the material information together with the component information, and export the model at once using a plugin. 
An example: A model with multi-layer component structure is presented and need to be exported into STEP files after the decomposition. The name last layer of the component is used as the file name, as “05_02_01_01_01_INLET_PIPE_FIXED”. Then, the material information is added into these names of the last-layer component, e.g. “SS316L” in this example. This name can be user-defined information. At the end the CAD solid of this component will be exported into a STEP file, and the file name is “05_02_01_01_01_INLET_PIPE_FIXED_SS316L”. 
The model grouped export plugin loops the whole model and find the last layer of component that contains CAD solids. There is an exceptional case, that is a component contains both solid and component. In this case, the name of this component is used for exporting the solid, while the sub-components it contains will be exported into other files. In this way, the information of the component (functional) and the material will be transfer to the STEP file. In the import step, the McCad Program use the file name as group name, and these groups will be assigned with unique materials for each of them. With the group name information provided, the user would have less problem in assigning the correct materials. 

## Lost particle visualization (lost_particle_track.scscript)

Identifying lost particle in the geometry is a step after generating the MCNP input file. Using the location and direction the lost particle travels, users can easily identify the reason of the lost particle, fix them either in the MCNP input geometry, or fix them in the CAD and convert again the MCNP input file. 

There are several feature provided by this lost particle visualization plugin: 
•	It visualizes the details historical tracks if the they are provided. Usually first 10 lost particles for each processors are provided in the MCNP output file, they can be used to detect some tricky lost particles which are not originate from the geometry error but due to the MCNP bugs. An example is shown which has lost particle in problem-free geometry. 
•	It produces the lost particle location as well as the tracks. They are saved in different folders, so that they are be visualized independently. Actually, the lost particle location (point mode)  is more useful to identify the geometry problem. 
•	Visualize the tracks on the top layer above the geometry, or the same layer with the geometry. Visualize the lost particle location on the top of the geometry is easy to locate the problem, instead of they are hidden by the structure. 

The processing of tens of thousands of lost particles might be time consuming. It is advised to first extract the lost particle output and save them in an individual file, and keep reasonable number of lost particles for the visualization. In practice, reading and visualization of 1000 lost particle can be done in minutes.  




