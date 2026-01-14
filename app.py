import streamlit as st
from PIL import Image
import exifread
import hashlib
from io import BytesIO
import urllib.parse

def google_search_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}"

def generate_google_dorks(term):
    dorks = {
        "Arquivos Sensíveis": [
            f'site:{term} filetype:pdf',
            f'site:{term} filetype:xls',
            f'site:{term} filetype:doc'
        ],
        "Diretórios Expostos": [
            f'site:{term} intitle:"index of"',
            f'site:{term} intitle:"parent directory"'
        ],
        "Credenciais e Vazamentos": [
            f'"{term}" password',
            f'"{term}" credentials',
            f'"{term}" leaked'
        ],
        "Tecnologia / Infra": [
            f'site:{term} inurl:admin',
            f'site:{term} inurl:login'
        ]
    }

    return dorks


def extract_metadata(uploaded_file):
    metadata = {}

    try:
        metadata["Nome do Arquivo"] = uploaded_file.name
        metadata["Tipo do Arquivo"] = uploaded_file.type
        metadata["Tamanho do Arquivo (Bytes)"] = uploaded_file.size

        if uploaded_file.type.startswith("image"):
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)

            metadata["Formato/Extensão"] = image.format
            metadata["Modo"] = image.mode
            metadata["Tamanho da Imagem"] = image.size

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
    report.append("=== AI-AutoReport | Análise Forense ===\n")

    report.append("[File Information]")
    report.append(f"Nome do Arquivo: {metadata.get('Nome do Arquivo')}")
    report.append(f"Tipo do Arquivo: {metadata.get('Tipo do Arquivo')}")
    report.append(f"Tamanho (bytes): {metadata.get('Tamanho do Arquivo (Bytes)')}\n")

    report.append("[Hashes]")
    for k, v in hashes.items():
        report.append(f"{k}: {v}")
    report.append("")

    report.append("[Metadata]")
    for k, v in metadata.items():
        if k == "exifTool":
            report.append("Dados EXIF:")
            if v:
                for exif_k, exif_v in v.items():
                    report.append(f"  - {exif_k}: {exif_v}")
            else:
                report.append("  Nenhum dado EXIF encontrado.")
        elif k not in ["Nome do Arquivo", "Tipo do Arquivo", "Tamanho do Arquivo"]:
            report.append(f"{k}: {v}")

    report.append("\n[Resumo]")
    report.append(
        "Esse relatório foi gerado automaticamente utilizando EXIFTOOL, PIL e HashLib. "
        "Uso jurídico e validação legal deve ser feita mediante a aprovação de um profissional qualificado."
    )

    return "\n".join(report)



st.set_page_config(
    page_title="OSINT-AutoReport",
    layout="wide"
)

st.title("Análise de Metadados")
st.caption("Ferramenta automatizada para análise Forense de arquivos e geração de Relatórios Técnicos.")

uploaded_file = st.file_uploader(
    "Envie um arquivo para análise de Metadados.",
    type=["jpg", "jpeg", "png", "pdf", "txt"]
)

if uploaded_file:
    st.success("Arquivo enviado com sucesso! ✅")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Metadata")
        metadata = extract_metadata(uploaded_file)
        st.json(metadata)

    with col2:
        st.subheader("Hashes")
        hashes = calculate_hashes(uploaded_file)
        st.json(hashes)

    if st.button("Gerar Relatório PDF"):
        report = generate_report(metadata, hashes)
        st.subheader("Relatório:")
        st.text_area("", report, height=500)

st.title("Busca - Google Dorks")
st.caption("Geração de Google Dorks.")

search_term = st.text_input(
    "Informe o termo para ser pesquisado.",
    placeholder='ex: Alexandre de Moraes, gov.com, lula@brasil.com'
)

if search_term:
    st.subheader("Google Dorks Gerados")

    dorks = generate_google_dorks(search_term)

    for category, queries in dorks.items():
        with st.expander(category):
            for q in queries:
                google_url = f"https://www.google.com/search?q={q}"
                st.markdown(f"- [{q}]({google_url})")

