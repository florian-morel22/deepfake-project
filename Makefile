
clone:
	git clone https://github.com/florian-morel22/REFace.git
	git clone https://github.com/taognt/FaceXRay.git
	git clone https://github.com/GroBonnet/e4s-faceswap-dataset.git
	git clone https://github.com/taognt/DeepFakeDetection
	git clone https://github.com/Barbossa972/Face_Swapping_VQVAE.git

setup:
	pip install -r requirements.txt	

	cd FaceXRay && pip install -r requirements.txt
	cd REFace && make setup
	

demo-run-server:
	srun --pty --time=04:00:00 --partition=ENSTA-l40s --gpus=1 python server.py

demo-run-client:
	streamlit run client.py
