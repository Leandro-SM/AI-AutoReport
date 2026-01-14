import streamlit as st
from PIL import Image
import exifread
import hashlib
import urllib.parse

st.set_page_config(
    page_title="AI-AutoReport",
    page_icon="🕵️",
    layout="wide"
)

st.markdown("## 🕵️ AI-AutoReport")
st.caption("Automated Forensic & OSINT Analysis Tool")
st.divider()

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
    return f"https://www.google.com/search?q={urllib.parse.quote(query)}"


def generate_google_dorks(term):
    quoted_term = f'"{term}"'
    site_term = f"site:{term}"

    return {
        "Menções Diretas (Texto)": [
            quoted_term,
            f'{quoted_term} password',
            f'{quoted_term} senha',
            f'{quoted_term} credentials',
            f'{quoted_term} leaked',
            f'{quoted_term} cpf',
            f'{quoted_term} email'
        ],
        "Arquivos Relacionados": [
            f'{quoted_term} filetype:pdf',
            f'{quoted_term} filetype:xls',
            f'{quoted_term} filetype:doc',
            f'{quoted_term} filetype:txt'
        ],
        "URLs Sensíveis (site:)": [
            f'{site_term} inurl:admin',
            f'{site_term} inurl:login',
            f'{site_term} inurl:password',
            f'{site_term} intitle:"index of"'
        ],
        "Redes Sociais": [
            f'site:instagram.com {quoted_term}',
            f'site:linkedin.com {quoted_term}',
            f'site:github.com {quoted_term}',
            f'site:reddit.com {quoted_term}'
        ]
    }


def extract_metadata(uploaded_file):
    metadata = {
        "Nome do Arquivo": uploaded_file.name,
        "Tipo do Arquivo": uploaded_file.type,
        "Tamanho (Bytes)": uploaded_file.size
    }

    try:
        if uploaded_file.type.startswith("image"):
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)

            metadata["Formato"] = image.format
            metadata["Modo"] = image.mode
            metadata["Dimensões"] = image.size

            uploaded_file.seek(0)
            exif_tags = exifread.process_file(uploaded_file, details=False)
            metadata["EXIF"] = {str(k): str(v) for k, v in exif_tags.items()}

    except Exception as e:
        metadata["Erro"] = str(e)

    return metadata


def calculate_hashes(uploaded_file):
    uploaded_file.seek(0)
    data = uploaded_file.read()

    return {
        "MD5": hashlib.md5(data).hexdigest(),
        "SHA1": hashlib.sha1(data).hexdigest(),
        "SHA256": hashlib.sha256(data).hexdigest()
    }


def generate_report(metadata, hashes):
    report = ["=== AI-AutoReport | Análise Forense ===\n"]

    report.append("[Arquivo]")
    for k, v in metadata.items():
        report.append(f"{k}: {v}")

    report.append("\n[Hashes]")
    for k, v in hashes.items():
        report.append(f"{k}: {v}")

    report.append(
        "\n[Resumo]\nRelatório gerado automaticamente. "
        "Validação legal deve ser feita por profissional qualificado."
    )

    return "\n".join(report)

uploaded_file = st.file_uploader(
    "📁 Envie um arquivo para análise",
    type=["jpg", "jpeg", "png", "pdf", "txt"]
)

tab1, tab2, tab3 = st.tabs([
    "🔬 Análise Forense",
    "🌐 OSINT",
    "📄 Relatório"
])

with tab1:
    st.subheader("Análise Forense")

    if uploaded_file:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Metadata")
            metadata = extract_metadata(uploaded_file)
            st.json(metadata, expanded=False)

        with col2:
            st.markdown("### Hashes")
            hashes = calculate_hashes(uploaded_file)
            st.json(hashes)
    else:
        st.info("Envie um arquivo para iniciar a análise forense.")

with tab2:
    st.subheader("OSINT – Google Dorks")

    search_term = st.text_input(
        "Termo de busca",
        placeholder="Nome, e-mail, domínio, empresa"
    )

    if search_term:
        dorks = generate_google_dorks(search_term)

        for category, queries in dorks.items():
            with st.expander(category):
                for q in queries:
                    st.markdown(f"- [{q}]({google_search_url(q)})")

    st.divider()
    st.subheader("OSINT – Insecam")

    selected_country = st.selectbox(
        "Selecione o país",
        list(INSECAM_COUNTRIES.keys())
    )

    if selected_country:
        code = INSECAM_COUNTRIES[selected_country]
        st.markdown(
            f"🔗 [Acessar Insecam – {selected_country}](http://www.insecam.org/en/bycountry/{code}/)"
        )
