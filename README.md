This is a repository for Timothy and Lucas to work on the Simulator of Urban MObility (SUMO) 
This will be dedicated to Timothy and Lucas's Science fair project

(Due 01-02-2024)

SUMO INSTALL:
1. go to the website https://sumo.dlr.de/docs/Downloads.php and click the download for "sumo-win64-1.18.0.msi"
2. once done downloading, open the file. this may prompt a windows message saying "windows protected your pc"
3. click more info and then click "run anyways"
4. follow the instructions in the setup wizard (Note:make sure you have the option "add to path" enabled or else functions through the CMD will not work properly)
5. finish the install

Example 1 instructions:

Go to Virtual Studio Code and on the left, click the 3rd tab to the top and click clone repository.
then copy https://github.com/HelloCodeLuc/Sumo-Code.git into the text field. 
it will ask for a directory and you can create a new file which you can select.
all the files should now exist in that folder.
create a file named output

Next you need to run the netconvert command.  Open a cmd prompt.
> cd to route directory
> mkdir out
> cd out
> netconvert --node-files ../Examples/install_test/my_nodes.nod.xml --edge-files ../Examples/install_test/edge_code.edg.xml -t ../Examples/install_test/my_type.typ.xml -o my_net.net.xml

the net file should be ready.

you may now click the "my_config-file.sumocfg" to run the simulation and confirm it is correct
