# ASLHackfest
Adversarial Science Lab's repository for the DARPA SDR Hackfest

## Installation

### python3
pip3 install .

### python2
sudo pip install .

## README for gr-uaslink?
Step to running flowgraph:

1. Start flowgraph on RPI:
	ssh root@192.168.10.5  
	cd gr-uaslink/apps/  
	./uhd_psk_burst_control_rpi.grc
	
2. Start the GUI controller: 

	cd gr-uaslink/apps/  
	python control_gui_override_control.py 

3. Start the aslsitlstub.grc flowgraph: 

	cd gr-uaslink/apps/  
	gnuradio-companion asl_sitl_stub.grc

4. Fly sitl using GUI controller.
