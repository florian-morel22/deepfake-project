import torch

from PIL import Image
from datetime import datetime
from REFace.our_work.scripts.inference import REFace
from demo.api_server import gmail_send_message, listen_gmail, get_images_from_gmail

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
generator = REFace(
    device=device,
    config_path="demo/reface_config.yaml",
    ckpt_path="REFace/models/REFace/checkpoints/last.ckpt",
    faceParsing_ckpt="REFace/Other_dependencies/face_parsing/79999_iter.pth",
    dlib_landmark_path="REFace/Other_dependencies/DLIB_landmark_det/shape_predictor_68_face_landmarks.dat",
)

if __name__ == '__main__':

    # TO TEST WITH LOCAL IMAGES
    target = Image.open("REFace/datasets/CelebAMask-HQ/CelebA-HQ-img/0.jpg").convert("RGB")
    source = Image.open("REFace/datasets/CelebAMask-HQ/CelebA-HQ-img/1.jpg").convert("RGB")
    swapped = generator.face_swapp(source, target)

    ref_date = datetime.now()
    blacklist_ids = []

    print("SERVER READY")

    while True:

        message_id, images_id = listen_gmail("Images", ref_date=ref_date, blacklist_ids=blacklist_ids) # loop until trigger
        blacklist_ids.append(message_id) # Do not trigger 2 times the same email

        source, target = get_images_from_gmail(message_id, images_id)
        swapped = generator.face_swapp(source, target)

        gmail_send_message(swapped, key_word="Swapp")
    