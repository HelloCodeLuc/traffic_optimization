
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'CONTROL_GUI'))
import plot_timing_changes

#output_dir = "out\\2025_03_30_15_01_47"
output_dir = "out\\2025_03_30_20_45_41"
junction_coords_file = f"{output_dir}\\GUI_junction_coordinates.csv"
network_file = "simple_network/simple_network.net.xml" 
optimize_network_averages_txt = f'{output_dir}/TRAIN_OPTIMIZATION/network_averages.txt'
network_averages = optimize_network_averages_txt

coord_differences = plot_timing_changes.coordinates_to_diff_of_offset_and_greenlight (f"NETWORKS/{network_file}", junction_coords_file, network_averages)


# school extended
#    <connection from="-E0" to="E42" fromLane="0" toLane="0" via=":J11_0_0" tl="mcnaughton_keele" linkIndex="5" dir="r" state="o"/>

# simple network
#    <connection from="-E3" to="E0" fromLane="0" toLane="0" via=":main1_8_0" tl="main" linkIndex="8" dir="l" state="o"/>
#    <connection from="-E4" to="-E2" fromLane="0" toLane="0" via=":main2_0_0" tl="main_2" linkIndex="0" dir="r" state="O"/>