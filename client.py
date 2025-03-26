import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from demo.utils import Image2bytes
from datetime import datetime, timezone
from demo.api_client import get_images_from_gmail, listen_gmail

pred_visu = ["REAL", "FAKE"]
pred_color = ["green", "red"]
predictions = ["0", "1"]


def show_masks(image: np.ndarray):
    fig, ax = plt.subplots()
    ax.imshow(image, cmap="jet")
    ax.axis("off")  # Hide axis for better visualization
    st.pyplot(fig)


def main():


    if "ref_date" not in st.session_state:
        st.session_state.ref_date = datetime.now(timezone.utc)
        st.session_state.source = None
        st.session_state.target = None
        st.session_state.swapp = None
        
        st.session_state.masks = None
        st.session_state.faceXray_pred = None
        st.session_state.mesonet_pred = None


    st.title('Face swapp Machine')

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Load Images"):
            message_id, images_id, _ = listen_gmail("Image", ref_date=st.session_state.ref_date)
            images_pil = get_images_from_gmail(message_id, images_id)
            images_bytes = [Image2bytes(img) for img in images_pil]
            st.session_state.source = images_bytes[0]
            st.session_state.target = images_bytes[1]
            st.session_state.swapp = None
            st.session_state.masks = None
            st.session_state.faceXray_pred = None
            st.session_state.mesonet_pred = None

    with col2:
        if st.button('Swap Faces'):
            message_id, images_id, _ = listen_gmail("Swapp", ref_date=st.session_state.ref_date)
            images_pil = get_images_from_gmail(message_id, images_id)
            images_bytes = [Image2bytes(img) for img in images_pil]
            st.session_state.swapp = images_bytes[0]
    with col3:
        if st.button('Detect Fakes'):
            message_id, images_id, text_content = listen_gmail("Masks", ref_date=st.session_state.ref_date)
            images_pil = get_images_from_gmail(message_id, images_id)
            images_numpy = [np.array(img) for img in images_pil]
            st.session_state.masks = images_numpy
            print(f"text content >>{text_content}<<")
            print(f"text split >>{text_content.split("\n")}<<")
            st.session_state.faceXray_pred = [
                int(pred.strip()[0]) 
                for pred in text_content.split("\n")
                if pred.strip() != ""
            ]
            st.session_state.mesonet_pred = [
                int(pred.strip()[2]) 
                for pred in text_content.split("\n")
                if pred.strip() != ""
            ]

    st.divider()

    source_col, target_col, swapped_col = st.columns([1, 1, 1], gap="large")

    with source_col:
        st.header('Source')

        if st.session_state.source is not None:
            st.image(st.session_state.source)

        if st.session_state.masks is not None:
            st.subheader(
                f"{pred_visu[st.session_state.mesonet_pred[0]]}", 
                divider=pred_color[st.session_state.mesonet_pred[0]]
            )
            st.subheader(
                f"{pred_visu[st.session_state.faceXray_pred[0]]}", 
                divider=pred_color[st.session_state.faceXray_pred[0]]
            )
            show_masks(st.session_state.masks[0])

    with target_col:
        st.header('Target')

        if st.session_state.target is not None:
            st.image(st.session_state.target)

        if st.session_state.masks is not None:
            st.subheader(
                f"{pred_visu[st.session_state.mesonet_pred[1]]}", 
                divider=pred_color[st.session_state.mesonet_pred[1]]
            )
            st.subheader(
                f"{pred_visu[st.session_state.faceXray_pred[1]]}", 
                divider=pred_color[st.session_state.faceXray_pred[1]]
            )
            show_masks(st.session_state.masks[1])


    with swapped_col:
        st.header('Swapp')

        if st.session_state.swapp is not None:
            st.image(st.session_state.swapp)

        if st.session_state.masks is not None:
            st.subheader(
                f"{pred_visu[st.session_state.mesonet_pred[2]]}", 
                divider=pred_color[st.session_state.mesonet_pred[2]]
            )
            st.subheader(
                f"{pred_visu[st.session_state.faceXray_pred[2]]}", 
                divider=pred_color[st.session_state.faceXray_pred[2]]
            )
            show_masks(st.session_state.masks[2])


if __name__ == '__main__':
    main()