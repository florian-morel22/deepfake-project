import torch

from PIL import Image
from datetime import datetime, timezone
from demo.api_server import gmail_send_message, listen_gmail, get_images_from_gmail

from FaceXRay.inference_hf import inference
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

        message_id, images_id = listen_gmail("Images", ref_date=ref_date, blacklist_ids=blacklist_ids) # loop until trigger
        blacklist_ids.append(message_id) # Do not trigger 2 times the same email

        source, target = get_images_from_gmail(message_id, images_id)
        swapped = generator.face_swapp(source, target)

        gmail_send_message([swapped], key_word="Swapp")

        # Detection
        masks, predictions = [], []
        for image in [source, target, swapped]:

            mask, prediction = inference(image, device=device, save=False)
            masks.append(mask)
            predictions.append(str(prediction))

        text_content = "\n".join(predictions)
        gmail_send_message(masks, text_content=text_content, key_word="Masks")
