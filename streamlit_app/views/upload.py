import streamlit as st

import api_client

st.title("Upload Document")
st.caption(
    "Supported formats: PDF, PNG, JPG, JPEG. Scanned pages and images are "
    "OCR'd automatically with Groq Vision."
)

review_mode = st.checkbox(
    "Preview & correct extracted text before indexing",
    value=False,
    help="Useful for handwritten notes or scanned pages where OCR may need a correction.",
)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "application/octet-stream"

    if not review_mode:
        if st.button("Upload & Index", type="primary"):
            with st.spinner("Extracting text and indexing..."):
                try:
                    result = api_client.upload_document(
                        uploaded_file.name, file_bytes, mime_type
                    )
                except api_client.APIError as exc:
                    st.error(f"Upload failed: {exc}")
                else:
                    st.success("Document indexed successfully.")
                    st.write(f"Chunks created: {result['chunks']}")

    else:
        if st.button("Extract Text", type="primary"):
            with st.spinner("Extracting text..."):
                try:
                    st.session_state.preview_data = api_client.preview_upload(
                        uploaded_file.name, file_bytes, mime_type
                    )
                except api_client.APIError as exc:
                    st.error(f"Extraction failed: {exc}")
                    st.session_state.preview_data = None

        preview = st.session_state.preview_data

        if preview:
            st.subheader("Review Extracted Text")
            st.caption(f"Extraction method: {preview['extraction_method']}")

            if preview.get("image_url"):
                st.image(
                    api_client.file_url(preview["image_url"]),
                    caption="Original image",
                    width=350,
                )

            edited_pages = []
            for page in preview["pages"]:
                edited_text = st.text_area(
                    f"Page {page['page']}",
                    value=page["text"],
                    height=150,
                    key=f"page_text_{preview['document_id']}_{page['page']}",
                )
                edited_pages.append({"page": page["page"], "text": edited_text})

            if st.button("Confirm & Index", type="primary"):
                payload = {
                    "document_id": preview["document_id"],
                    "filename": preview["filename"],
                    "extension": preview["extension"],
                    "extraction_method": preview["extraction_method"],
                    "pages": edited_pages,
                }
                with st.spinner("Indexing..."):
                    try:
                        result = api_client.confirm_upload(payload)
                    except api_client.APIError as exc:
                        st.error(f"Indexing failed: {exc}")
                    else:
                        st.success("Document indexed successfully.")
                        st.write(f"Chunks created: {result['chunks']}")
                        st.session_state.preview_data = None
