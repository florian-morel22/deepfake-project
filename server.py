import os
import sys
import torch

from PIL import Image
from datetime import datetime, timezone
from demo.api_server import gmail_send_message, listen_gmail, get_images_from_gmail

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'DeepFakeDetection/Detection_classifier/mesogip_inference')))
from DeepFakeDetection.Detection_classifier.mesogip_inference.mesogip_function import mesogip_inference 

# Add the directory containing the 'facexray' module to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'FaceXRay')))
from FaceXRay.inference_hf import inference

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'REFace')))
from REFace.our_work.scripts.inference import REFace

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
generator = REFace(
    device=device,
    config_path="demo/reface_config.yaml",
    ckpt_path="REFace/models/REFace/checkpoints/last.ckpt",
    faceParsing_ckpt="REFace/Other_dependencies/face_parsing/79999_iter.pth",
    dlib_landmark_path="REFace/Other_dependencies/DLIB_landmark_det/shape_predictor_68_face_landmarks.dat",
)

if __name__ == '__main__':

    # # TO TEST WITH LOCAL IMAGES
    # target = Image.open("REFace/datasets/CelebAMask-HQ/CelebA-HQ-img/0.jpg").convert("RGB")
    # source = Image.open("REFace/datasets/CelebAMask-HQ/CelebA-HQ-img/1.jpg").convert("RGB")
    # swapped = generator.face_swapp(source, target)
    # mask, prediction = inference(target, device=device, save=False)
    # gmail_send_message([mask], key_word="Mask")


    ref_date = datetime.now(timezone.utc)
    blacklist_ids = []

    print("SERVER READY")

    while True:

        message_id, images_id, _ = listen_gmail("Images", ref_date=ref_date, blacklist_ids=blacklist_ids) # loop until trigger
        blacklist_ids.append(message_id) # Do not trigger 2 times the same email

        source, target = get_images_from_gmail(message_id, images_id)
        swapped = generator.face_swapp(source, target)

        gmail_send_message([swapped], key_word="Swapp")

        # Detection FaceXRay + Mesogip
        masks, pred_faceXray, pred_mesonet = [], [], []
        for image in [source, target, swapped]:

            mask, prediction = inference(image, device=device, save=False, verbose=False)
            masks.append(mask)
            pred_faceXray.append(str(prediction))

            prediction = mesogip_inference(image)
            pred_mesonet.append(str(prediction))

        text_content = "\n".join([fxr + " " + mes for fxr, mes in zip(pred_faceXray, pred_mesonet)])
        gmail_send_message(masks, text_content=text_content, key_word="Masks")
