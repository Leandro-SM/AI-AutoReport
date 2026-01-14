import streamlit as st
from PIL import Image
import exifread
import hashlib
from io import BytesIO

def extract_metadata(uploaded_file):
    metadata = {}

    try:
        metadata["filename"] = uploaded_file.name
        metadata["content_type"] = uploaded_file.type
        metadata["size_bytes"] = uploaded_file.size

        if uploaded_file.type.startswith("image"):
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)

            metadata["image_format"] = image.format
            metadata["image_mode"] = image.mode
            metadata["image_size"] = image.size

            uploaded_file.seek(0)
            exif_tags = exifread.process_file(uploaded_file, details=False)
            metadata["exif"] = {str(k): str(v) for k, v in exif_tags.items()}

    except Exception as e:
        metadata["error"] = str(e)

    return metadata


def calculate_hashes(uploaded_file):
    hashes = {
        "MD5": hashlib.md5(),
        "SHA1": hashlib.sha1(),
        "SHA256": hashlib.sha256()
    }

    uploaded_file.seek(0)
    data = uploaded_file.read()

    for h in hashes.values():
        h.update(data)

    return {name: h.hexdigest() for name, h in hashes.items()}


def generate_report(metadata, hashes):
    report = []
    report.append("=== AI-AutoReport | Forensic Analysis ===\n")

    report.append("[File Information]")
    report.append(f"Filename: {metadata.get('filename')}")
    report.append(f"Content-Type: {metadata.get('content_type')}")
    report.append(f"Size (bytes): {metadata.get('size_bytes')}\n")

    report.append("[Cryptographic Hashes]")
    for k, v in hashes.items():
        report.append(f"{k}: {v}")
    report.append("")

    report.append("[Metadata]")
    for k, v in metadata.items():
        if k == "exif":
            report.append("EXIF Data:")
            if v:
                for exif_k, exif_v in v.items():
                    report.append(f"  - {exif_k}: {exif_v}")
            else:
                report.append("  No EXIF data found")
        elif k not in ["filename", "content_type", "size_bytes"]:
            report.append(f"{k}: {v}")

    report.append("\n[Conclusion]")
    report.append(
        "This report was generated automatically and contains raw forensic data. "
        "Interpretation and legal validation should be performed by a qualified analyst."
    )

    return "\n".join(report)



st.set_page_config(
    page_title="AI-AutoReport",
    layout="wide"
)

st.title("AI-AutoReport")
st.caption("Automated Forensic Report Generator")

uploaded_file = st.file_uploader(
    "Upload a file for forensic analysis",
    type=["jpg", "jpeg", "png", "pdf", "txt"]
)

if uploaded_file:
    st.success("File uploaded successfully")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Metadata Preview")
        metadata = extract_metadata(uploaded_file)
        st.json(metadata)

    with col2:
        st.subheader("Hashes")
        hashes = calculate_hashes(uploaded_file)
        st.json(hashes)

    if st.button("Generate Forensic Report"):
        report = generate_report(metadata, hashes)
        st.subheader("Forensic Report")
        st.text_area("", report, height=500)
