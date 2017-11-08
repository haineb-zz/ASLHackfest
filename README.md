# ASLHackfest
Adversarial Science Lab's repository for the DARPA SDR Hackfest

Step to running flowgraph:

1. Start vehicle sim: sim_vehicle.py --console --map --aircraft test

2. Start the GUI controller: ./control_gui_override_control.py 

3. Start the hainesb Gateway: python run.py 

4. Start the aslsitlstub.grc flowgraph: gnuradio-companion asl_sitl_stub.grc

5. Fly sitl using GUI controller.
