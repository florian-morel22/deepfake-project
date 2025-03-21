setup:
	pip install -r requirements.txt

	git clone https://github.com/florian-morel22/REFace.git
	git clone https://github.com/taognt/FaceXRay.git

	cd FaceXRay && pip install -r requirements.txt
	cd REFace && make setup
	
	git clone https://github.com/taognt/FaceXRay.git

	pip install -r FaceXRay/requirements.txt

demo-run-server:
	srun --pty --time=04:00:00 --partition=ENSTA-l40s --gpus=1 python server.py

demo-run-client:
	streamlit run client.py
