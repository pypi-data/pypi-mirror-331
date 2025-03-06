import asyncio
import base64
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

import pdf2u.high_level
from pdf2u.const import TranslationService, get_cache_file_path
from pdf2u.document_il.translator.translator import (
    BaseTranslator,
    BingTranslator,
    GoogleTranslator,
    OpenAITranslator,
    set_translate_rate_limiter,
)
from pdf2u.docvision.doclayout import DocLayoutModel, OnnxModel
from pdf2u.translation_config import TranslationConfig


def create_pdf_html(base64_pdf: str) -> str:
    """Custom HTML/CSS for PDF display with page number"""
    pdf_display = f"""
        <div style="display: flex; justify-content: center; width: 100%;">
            <embed
                type="application/pdf"
                src="data:application/pdf;base64,{base64_pdf}#page=1"
                width="100%"
                height="800px"
                style="border: 1px solid #ccc;"
            />
        </div>
    """
    return pdf_display


@st.cache_resource
def load_onnx_model() -> OnnxModel:
    return DocLayoutModel.load_onnx()


@st.cache_resource
def init_backend() -> None:
    pdf2u.high_level.init()


async def process_file(config: TranslationConfig, debug: bool) -> None:
    """Process a single PDF file."""
    async for event in pdf2u.high_level.async_translate(config):
        if event["type"] == "finish":
            result = event["translate_result"]
            return result


def translate_pdf(
    input_file: Path,
    output_dir: Path,
    service: TranslationService = TranslationService.GOOGLE,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
    openai_base_url: str | None = None,
    source_lang: str = "en",
    target_lang: str = "zh",
    qps: int = 10,
    ignore_cache: bool = False,
) -> tuple[Path, Path] | None:
    """Translate PDF files using various translation services."""

    # Validate OpenAI settings
    if service == TranslationService.OPENAI and not openai_api_key:
        st.toast("Error: Must specify OpenAI API key (--openai-api-key)")
        return

    # Initialize translator
    translator: BaseTranslator
    if service == TranslationService.OPENAI:
        translator = OpenAITranslator(
            lang_in=source_lang,
            lang_out=target_lang,
            model=openai_model,
            base_url=openai_base_url,
            api_key=openai_api_key,
            ignore_cache=ignore_cache,
        )
    elif service == TranslationService.BING:
        translator = BingTranslator(
            lang_in=source_lang, lang_out=target_lang, ignore_cache=ignore_cache
        )
    else:  # Google
        translator = GoogleTranslator(
            lang_in=source_lang, lang_out=target_lang, ignore_cache=ignore_cache
        )

    # Set translation rate limit
    set_translate_rate_limiter(qps)

    # Initialize document layout model
    doc_layout_model = load_onnx_model()

    # Get and validate font
    font_path = get_cache_file_path("source-han-serif-cn.ttf")
    if font_path:
        if not Path(font_path).exists():
            st.toast(f"Error: Font file not found: {font_path}")
            return
        if not str(font_path).endswith(".ttf"):
            st.toast(f"Error: Invalid font file: {font_path}")
            return

    config = TranslationConfig(
        input_file=str(input_file),
        font=font_path.as_posix() if font_path else None,
        output_dir=str(output_dir) if output_dir else None,
        translator=translator,
        debug=False,
        lang_in=source_lang,
        lang_out=target_lang,
        no_dual=False,
        no_mono=False,
        qps=qps,
        doc_layout_model=doc_layout_model,
        skip_clean=False,
        enhance_compatibility=False,
    )
    # Execute
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # 运行异步函数
        result = loop.run_until_complete(process_file(config, debug=False))
        translated_pdf = Path(result.mono_pdf_path) if result.mono_pdf_path else None
        bilingual_pdf = Path(result.dual_pdf_path) if result.dual_pdf_path else None

        if not translated_pdf or not bilingual_pdf:
            st.toast("Error: Translation failed")
            return

        return translated_pdf, bilingual_pdf
    finally:
        loop.close()


def reset_file_state() -> None:
    st.session_state.pdf_state = PDFState(original_pdf=st.session_state.uploaded_file)


def start_translate() -> None:
    """Translate Config InterFace"""
    st.session_state.pdf_state.start_translate = True
    st.toast(body="Translation started! 🎉")
    init_backend()
    # update config with session state
    for k, v in st.session_state.items():
        if k in asdict(st.session_state.config):
            st.session_state.config.__setattr__(k, v)
    config = st.session_state.config
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_output_dir = Path(tmp_dir)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(
                get_pdf_content(st.session_state.pdf_state.original_pdf, s_b=False)
            )
            tmp_input_file = Path(tmp_file.name)

            try:
                # invoke translation
                translated_pdf, bilingual_pdf = translate_pdf(
                    input_file=tmp_input_file,
                    output_dir=tmp_output_dir,
                    service=config.service,
                    openai_api_key=config.api_key
                    if config.service == TranslationService.OPENAI
                    else None,
                    source_lang=config.source_lang,
                    target_lang=config.target_lang,
                    qps=config.qps,
                    ignore_cache=config.ignore_cache,
                )
                with open(translated_pdf, "rb") as f:
                    translated_pdf_content = f.read()
                with open(bilingual_pdf, "rb") as f:
                    bilingual_pdf_content = f.read()

                # update session state
                st.session_state.pdf_state.translated_pdf = translated_pdf_content
                st.session_state.pdf_state.bilingual_pdf = bilingual_pdf_content
                st.session_state.pdf_state.translated = True
                st.session_state.pdf_state.start_translate = False

                st.toast("Translation completed! 🎉")
            except Exception as e:
                st.error(f"Translation failed: {str(e)}")
            finally:
                tmp_input_file.unlink()

    # # Test
    # translated_pdf_path = Path(__file__).parents[2] / "tests" / "data" / "sample.pdf"
    # st.session_state.pdf_state.translated_pdf = translated_pdf_path
    # st.session_state.pdf_state.bilingual_pdf = translated_pdf_path

    # st.session_state.pdf_state.translated = True
    # st.session_state.pdf_state.start_translate = False

    # st.toast(st.session_state.config)
    # st.toast(st.session_state.pdf_state)


def show_config_sidebar() -> None:
    with st.sidebar:
        st.title("PDF Translator")

        st.file_uploader(
            " ", type="pdf", key="uploaded_file", on_change=reset_file_state
        )

        if st.session_state.pdf_state.translated:
            create_download_buttons(
                st.session_state.pdf_state.translated_pdf,
                st.session_state.pdf_state.bilingual_pdf,
            )

        if st.session_state.pdf_state.original_pdf is not None:
            st.button(
                "🚀 Translate",
                type="primary",
                use_container_width=True,
                on_click=start_translate,
            )
        else:
            st.info("Please upload a PDF file to translate.")

        # st.divider()
        st.selectbox(
            "Service 🔄",
            options=["google", "openai", "bing"],
            key="service",
            help="select translation service",
        )

        if st.session_state.service == TranslationService.OPENAI:
            st.text_input(
                "OpenAI API Key 🔑",
                type="password",
                key="api_key",
                help="get your API key from OpenAI",
            )

        col1, col2 = st.columns(2)
        with col1:
            st.selectbox(
                "Origin 📖",
                options=["en", "zh", "ja", "ko", "fr", "de"],
                key="source_lang",
            )
        with col2:
            st.selectbox(
                "Target 📝",
                options=["zh", "en", "ja", "ko", "fr", "de"],
                key="target_lang",
            )

        st.number_input(
            "QPS limit ⚡",
            min_value=1,
            value=10,
            key="qps",
            help="queries per second limit",
        )

        col3, col4 = st.columns(2)
        with col3:
            st.toggle("No Cache 🚫", key="ignore_cache")


def create_download_buttons(translated_pdf: bytes, bilingual_pdf: bytes) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Translation Only",
            data=translated_pdf,
            file_name="translated.pdf",
            mime="application/pdf",
        )
    with col2:
        st.download_button(
            label="📥 Download Bilingual",
            data=bilingual_pdf,
            file_name="bilingual.pdf",
            mime="application/pdf",
        )


@dataclass
class Config:
    service: TranslationService = TranslationService.GOOGLE
    api_key: str = "sk-1234567890"
    source_lang: str = "en"
    target_lang: str = "zh"
    qps: int = 10
    ignore_cache: bool = False


@dataclass
class PDFState:
    translated: bool = False
    start_translate: bool = False
    original_pdf: UploadedFile = None
    translated_pdf: bytes = None
    bilingual_pdf: bytes = None


def init_session_state() -> None:
    """Initialize session state variables."""
    if "config" not in st.session_state:
        # translate config
        st.session_state.config = Config()

    if "pdf_state" not in st.session_state:
        st.session_state.pdf_state = PDFState()


@st.cache_data
def get_pdf_content(
    uploaded_file: UploadedFile | Path | bytes, s_b: bool = True
) -> str:
    if isinstance(uploaded_file, Path):
        with open(uploaded_file, "rb") as f:
            pdf_content = f.read()
    elif isinstance(uploaded_file, bytes):
        pdf_content = uploaded_file
    else:
        uploaded_file.seek(0)  # Reset file pointer
        pdf_content = uploaded_file.read()
    if s_b:
        return base64.b64encode(pdf_content).decode("utf-8")
    else:
        return pdf_content


def main() -> None:
    st.set_page_config(
        layout="wide", page_title="PDF Translator", initial_sidebar_state="expanded"
    )

    init_session_state()
    show_config_sidebar()

    if st.session_state.pdf_state.start_translate:
        with st.spinner("Translating..."):
            pass
    if st.session_state.pdf_state.original_pdf is not None:
        # st.toast(f"PDF uploaded! 📄{st.session_state.pdf_state.original_pdf.name}")
        # Display PDF
        if st.session_state.pdf_state.translated:
            st.markdown("#### 📝 Bilingual PDF")
            pdf_display_base64 = get_pdf_content(
                st.session_state.pdf_state.bilingual_pdf
            )
        else:
            st.markdown("#### 📄 Original PDF")
            pdf_display_base64 = get_pdf_content(
                st.session_state.pdf_state.original_pdf
            )
        pdf_display = create_pdf_html(pdf_display_base64)
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style='text-align: center; margin-top: 50px;'>
                <h3>👈 Please Upload PDF</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
