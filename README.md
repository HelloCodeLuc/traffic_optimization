This is a repository for Timothy and Lucas to work on the Simulator of Urban MObility (SUMO) 
This will be dedicated to Timothy and Lucas's Science fair project

(Due 01-02-2024)

SUMO INSTALL:
1. go to the website https://sumo.dlr.de/docs/Downloads.php and click the download for "sumo-win64-1.18.0.msi"
2. once done downloading, open the file. this may prompt a windows message saying "windows protected your pc"
3. click more info and then click "run anyways"
4. follow the instructions in the setup wizard
  4.5 make sure you have the option "add to path" enabled or else functions through the CMD will not work properly
5. finish the install

Example 1 instructions:
1. Create a new folder
2. Create a .txt file and insert the code from "Nodes Code (Example 1)"
3. Rename the file to "my_nodes.nod.xml (Make sure that the file extension is .XML or else will not work)
4. Create a .txt file and insert the code from "Edge Code (Example 1)"
5. Rename the file to "my_edge.edg.xml (Make sure that the file extension is .XML or else will not work)
6. Create a .txt file and insert the code from "Type Code (Example 1)"
7. Rename the file to "my_type.type.xml (Make sure that the file extension is .XML or else will not work)
8. go to the folder and at the top where it says the folder name, click on it and replace it with CMD
9. once CMD is opened, paste "> netconvert --node-files my_nodes.nod.xml --edge-files my_edge.edg.xml -t my_type.type.xml -o my_net.net.xml"
10. this should create a file called "my_net.net.xml. this is your network file. if this does not work consult Lucas for aid
11. Next, we need to create the route file. Create a new .txt file and copy the code from the "Route Code(Example 1)" into the file
12. Rename the file to "my_route.rou.xml" (Make sure the file extension is .XML)
13. Lastly we need to create the configuration file. This is the file where we can define different setups for the simulation
14. Create a new .txt file and copy the "Configuration Code(Example 1)" into the file
15. Rename the file to my_config_file.sumocfg (sumocfg is the file extension that sumo recognises as a simulation)

You can now run the simulation and confirm that everything is correct
