# ASLHackfest
Adversarial Science Lab's repository for the DARPA SDR Hackfest

Step to running flowgraph:

1. Start vehicle sim: 

	cd ardupilot/ArduCopter/
	python sim_vehicle.py --console --map --aircraft test

2. Start the GUI controller: 

	cd gr-uaslink/apps/
	python control_gui_override_control.py 

3. Start the hainesb Gateway: 

	cd ASLHackfest/
	python run.py 

4. Start the aslsitlstub.grc flowgraph: 

	cd gr-uaslink/apps/
	gnuradio-companion asl_sitl_stub.grc

5. Fly sitl using GUI controller.
