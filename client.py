import streamlit as st

from demo.utils import Image2bytes
from datetime import datetime, timezone
from demo.api_client import get_images_from_gmail, listen_gmail

def main():


    if "ref_date" not in st.session_state:
        st.session_state.ref_date = datetime.now(timezone.utc)
        st.session_state.source = None
        st.session_state.target = None
        st.session_state.swapp = None


    st.title('Face swapp Machine')
    st.divider()

    if st.button("Load Images"):
        message_id, images_id = listen_gmail("Image", ref_date=st.session_state.ref_date)
        images_pil = get_images_from_gmail(message_id, images_id)
        images_bytes = [Image2bytes(img) for img in images_pil]
        st.session_state.source = images_bytes[0]
        st.session_state.target = images_bytes[1]
        st.session_state.swapp = None

    
    if st.button('Swap Faces'):
        message_id, images_id = listen_gmail("Swapp", ref_date=st.session_state.ref_date)
        images_pil = get_images_from_gmail(message_id, images_id)
        images_bytes = [Image2bytes(img) for img in images_pil]
        st.session_state.swapp = images_bytes[0]

    source_col, target_col, swapped_col = st.columns([1, 1, 1], gap="large")

    with source_col:
        st.header('Source')

        if st.session_state.source is not None:
            st.image(st.session_state.source)

    with target_col:
        st.header('Target')

        if st.session_state.target is not None:
            st.image(st.session_state.target)


    with swapped_col:
        st.header('Swapp')

        if st.session_state.swapp is not None:
            st.image(st.session_state.swapp)



if __name__ == '__main__':
    main()