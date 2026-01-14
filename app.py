import streamlit as st
from PIL import Image
import exifread
import hashlib
from io import BytesIO
import urllib.parse

INSECAM_COUNTRIES = {
    "Brazil - BR": "br",
    "Canada - CA": "ca",
    "United States - US": "us",
    "Germany - DE": "de",
    "France - FR": "fr",
    "Italy - IT": "it",
    "Spain - ES": "es",
    "Japan - JP": "jp",
    "Russia - RU": "ru"
}

def google_search_url(query):
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}"

def generate_google_dorks(term):
    quoted_term = f'"{term}"'
    site_term = f"site:{term}"

    dorks = {
        "Menções Diretas (Texto)": [
            quoted_term,
            f'{quoted_term} password',
            f'{quoted_term} senha',
            f'{quoted_term} credentials',
            f'{quoted_term} user',
            f'{quoted_term} leaked',
            f'{quoted_term} cpf',
            f'{quoted_term} e-mail',
            f'{quoted_term} name'
        ],
        "Arquivos Relacionados": [
            f'{quoted_term} filetype:pdf',
            f'{quoted_term} filetype:xls',
            f'{quoted_term} filetype:doc',
            f'{quoted_term} filetype:xlsx',
            f'{quoted_term} filetype:docx',
            f'{quoted_term} filetype:php',
            f'{quoted_term} filetype:txt'
        ],
        "inUrl (site:)": [
            f'{site_term} inurl:admin',
            f'{site_term} inurl:login',
            f'{site_term} inurl:password',
            f'{site_term} inurl:cpf',
            f'{site_term} inurl:user',
            f'{site_term} inurl:wp-admin',
            f'{site_term} intitle:"index of"'
        ],
        "Redes Sociais": [
            f'site:instagram.com {quoted_term}',
            f'site:x.com {quoted_term}',
            f'site:facebook.com {quoted_term}',
            f'site:youtube.com {quoted_term}',
            f'site:deviantart.com {quoted_term}',
            f'site:github.com {quoted_term}',
            f'site:linkedin.com {quoted_term}',
            f'site:reddit.com {quoted_term}',
            f'site:tiktok.com {quoted_term}'
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

tab1, tab2, tab3 = st.tabs([
    "🔬 Forensic Analysis",
    "🌐 OSINT",
    "📄 Relatório"
])


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
    placeholder='ex: Nome, Tel, E-mail.'
)

if search_term:
    st.subheader("Google Dorks Gerados")

    dorks = generate_google_dorks(search_term)

    for category, queries in dorks.items():
        with st.expander(category):
            for q in queries:
                url = google_search_url(q)
                st.markdown(f"- [{q}]({url})", unsafe_allow_html=True)

st.title("OSINT - Insecam")
st.caption("Cameras indexadas publicamente.")

selected_country = st.selectbox(
    "Selecione o país",
    options=list(INSECAM_COUNTRIES.keys())
)

if selected_country:
    country_code = INSECAM_COUNTRIES[selected_country]
    insecam_url = f"http://www.insecam.org/en/bycountry/{country_code}/"

    st.markdown(
        f"🔗 [Acessar Insecam - {selected_country}]({insecam_url})",
        unsafe_allow_html=True
    )
