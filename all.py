# app.py
import streamlit as st
import zipfile
import io
import os
import html
from typing import Tuple, List
import requests
import concurrent.futures
import multiprocessing
import functools

# Try to import aksharamukha bindings (preferred)
AKSHARAMUKHA_AVAILABLE = False
try:
    from aksharamukha import transliterate as aksharamukha_trans
    AKSHARAMUKHA_AVAILABLE = True
except Exception:
    AKSHARAMUKHA_AVAILABLE = False

# -------------------------
# Full SCRIPT_MAP (user-provided)
# -------------------------
SCRIPT_MAP = {
    "Ahom": "Ahom",
    "Arabic": "Arab",
    "Ariyaka": "Ariyaka",
    "Assamese": "Assamese",
    "Avestan": "Avestan",
    "Balinese": "Balinese",
    "Batak Karo": "BatakKaro",
    "Batak Mandailing": "BatakManda",
    "Batak Pakpak": "BatakPakpak",
    "Batak Simalungun": "BatakSima",
    "Batak Toba": "BatakToba",
    "Bengali (Bangla)": "Bengali",
    "Bhaiksuki": "Bhaiksuki",
    "Brahmi": "Brahmi",
    "Buginese (Lontara)": "Buginese",
    "Buhid": "Buhid",
    "Burmese (Myanmar)": "Burmese",
    "Chakma": "Chakma",
    "Cham": "Cham",
    "Cyrillic (Russian)": "RussianCyrillic",
    "Devanagari": "Devanagari",
    "Dives Akuru": "DivesAkuru",
    "Dogra": "Dogra",
    "Elymaic": "Elym",
    "Ethiopic (Abjad)": "Ethi",
    "Gondi (Gunjala)": "GunjalaGondi",
    "Gondi (Masaram)": "MasaramGondi",
    "Grantha": "Grantha",
    "Grantha (Pandya)": "GranthaPandya",
    "Gujarati": "Gujarati",
    "Hanunoo": "Hanunoo",
    "Hatran": "Hatr",
    "Hebrew": "Hebrew",
    "Hebrew (Judeo-Arabic)": "Hebr-Ar",
    "Imperial Aramaic": "Armi",
    "Inscriptional Pahlavi": "Phli",
    "Inscriptional Parthian": "Prti",
    "Japanese (Hiragana)": "Hiragana",
    "Japanese (Katakana)": "Katakana",
    "Javanese": "Javanese",
    "Kaithi": "Kaithi",
    "Kannada": "Kannada",
    "Kawi": "Kawi",
    "Khamti Shan": "KhamtiShan",
    "Kharoshthi": "Kharoshthi",
    "Khmer (Cambodian)": "Khmer",
    "Khojki": "Khojki",
    "Khom Thai": "KhomThai",
    "Khudawadi": "Khudawadi",
    "Lao": "Lao",
    "Lao (Pali)": "LaoPali",
    "Lepcha": "Lepcha",
    "Limbu": "Limbu",
    "Mahajani": "Mahajani",
    "Makasar": "Makasar",
    "Malayalam": "Malayalam",
    "Manichaean": "Mani",
    "Marchen": "Marchen",
    "Meetei Mayek (Manipuri)": "MeeteiMayek",
    "Modi": "Modi",
    "Mon": "Mon",
    "Mongolian (Ali Gali)": "Mongolian",
    "Mro": "Mro",
    "Multani": "Multani",
    "Nabataean": "Nbat",
    "Nandinagari": "Nandinagari",
    "Newa (Nepal Bhasa)": "Newa",
    "Old North Arabian": "Narb",
    "Old Persian": "OldPersian",
    "Old Sogdian": "Sogo",
    "Old South Arabian": "Sarb",
    "Oriya (Odia)": "Oriya",
    "Pallava": "Pallava",
    "Palmyrene": "Palm",
    "Persian": "Arab-Fa",
    "PhagsPa": "PhagsPa",
    "Phoenician": "Phnx",
    "Psalter Pahlavi": "Phlp",
    "Punjabi (Gurmukhi)": "Gurmukhi",
    "Ranjana (Lantsa)": "Ranjana",
    "Rejang": "Rejang",
    "Rohingya (Hanifi)": "HanifiRohingya",
    "Roman (Baraha North)": "BarahaNorth",
    "Roman (Baraha South)": "BarahaSouth",
    "Roman (Colloquial)": "RomanColloquial",
    "Roman (DMG Persian)": "PersianDMG",
    "Roman (Harvard-Kyoto)": "HK",
    "Roman (IAST)": "IAST",
    "Roman (IAST: Pāḷi)": "IASTPali",
    "Roman (IPA Indic)": "IPA",
    "Roman (ISO 15919 Indic)": "ISO",
    "Roman (ISO 15919: Pāḷi)": "ISOPali",
    "Roman (ISO 233 Arabic)": "ISO233",
    "Roman (ISO 259 Hebrew)": "ISO259",
    "Roman (ITRANS)": "Itrans",
    "Roman (Library of Congress)": "RomanLoC",
    "Roman (Readable)": "RomanReadable",
    "Roman (SBL Hebrew)": "HebrewSBL",
    "Roman (SLP1)": "SLP1",
    "Roman (Semitic Typeable)": "Type",
    "Roman (Semitic)": "Latn",
    "Roman (Titus)": "Titus",
    "Roman (Velthuis)": "Velthuis",
    "Roman (WX)": "WX",
    "Samaritan": "Samr",
    "Santali (Ol Chiki)": "Santali",
    "Saurashtra": "Saurashtra",
    "Shahmukhi": "Shahmukhi",
    "Shan": "Shan",
    "Sharada": "Sharada",
    "Siddham": "Siddham",
    "Sinhala": "Sinhala",
    "Sogdian": "Sogd",
    "Sora Sompeng": "SoraSompeng",
    "Soyombo": "Soyombo",
    "Sundanese": "Sundanese",
    "Syloti Nagari": "SylotiNagri",
    "Syriac (Eastern)": "Syrn",
    "Syriac (Estrangela)": "Syre",
    "Syriac (Western)": "Syrj",
    "Tagalog": "Tagalog",
    "Tagbanwa": "Tagbanwa",
    "Tai Laing": "TaiLaing",
    "Takri": "Takri",
    "Tamil": "Tamil",
    "Tamil (Extended)": "TamilExtended",
    "Tamil Brahmi": "TamilBrahmi",
    "Telugu": "Telugu",
    "Thaana (Dhivehi)": "Thaana",
    "Thai": "Thai",
    "Tham (Lanna)": "TaiTham",
    "Tham (Lao)": "LaoTham",
    "Tham (Tai Khuen)": "KhuenTham",
    "Tham (Tai Lue)": "LueTham",
    "Tibetan": "Tibetan",
    "Tirhuta (Maithili)": "Tirhuta",
    "Ugaritic": "Ugar",
    "Urdu": "Urdu",
    "Vatteluttu": "Vatteluttu",
    "Wancho": "Wancho",
    "Warang Citi": "WarangCiti",
    "Zanabazar Square": "ZanabazarSquare",
}

# -------------------------
# Config
# -------------------------
SOURCE_ID = "ISO"  # ISO 15919 input
MAX_WORKERS = 6     # number of processes to use in the pool

# -------------------------
# Utilities
# -------------------------
def sanitize_filename(s: str) -> str:
    """Make a safe filename / folder name (alphanumeric, dash, underscore)."""
    keep = []
    for c in s:
        if c.isalnum() or c in (" ", "_", "-"):
            keep.append(c)
    return "".join(keep).strip().replace(" ", "_")

# Top-level worker function must be picklable
def transliterate_worker(args: Tuple[str, str]) -> str:
    """
    Worker to transliterate a single text to a target script_id.
    args = (text, target_script_id)
    Returns the converted text (string).
    """
    text, target_id = args
    # Try local aksharamukha if available
    if AKSHARAMUKHA_AVAILABLE:
        try:
            # aksharamukha python binding typical API: process(src, tgt, text)
            return aksharamukha_trans.process(SOURCE_ID, target_id, text)
        except Exception:
            pass

    # Fallback to HTTP API (public)
    # Note: endpoint and response format may vary; adjust if needed.
    try:
        api_url = "https://aksharamukha.appspot.com/api/transliterate"
        payload = {"source": SOURCE_ID, "target": target_id, "text": text}
        r = requests.post(api_url, json=payload, timeout=30)
        if r.status_code == 200:
            # The public endpoint returns plain text body (observed) — attempt to parse safely
            # if JSON with {"text": "..."} is returned, handle that too.
            try:
                return r.json().get("text", r.text)
            except Exception:
                return r.text
    except Exception:
        pass

    # If all else fails, return original text
    return text

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="ISO15919 → Multi-Script (parallel)", layout="wide")
st.title("ISO 15919 → Multi-Script Transliterator (parallel)")

st.markdown(
    "Upload up to 200 UTF-8 `.txt` files in ISO 15919 romanization. "
    "Choose **Convert to ALL scripts** to produce a single ZIP where each script has its own folder. "
    "This runs transliteration in parallel using multiple processes (default 6)."
)

uploaded_files = st.file_uploader("Upload .txt files (multiple)", type=["txt"], accept_multiple_files=True)
convert_all = st.checkbox("Convert to ALL scripts at once (Option A: subfolders per script)", value=True)
single_target = None
if not convert_all:
    single_target = st.selectbox("Select target script", sorted(list(SCRIPT_MAP.keys())))

workers = st.number_input("Number of worker processes (max 12)", min_value=1, max_value=12, value=MAX_WORKERS, step=1)

start_btn = st.button("Start conversion")

# small helper to read uploaded file content safely
def read_file_content(uploaded_file) -> str:
    raw = uploaded_file.read()
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            text = raw.decode(enc)
            return text
        except Exception:
            continue
    # fallback
    try:
        return raw.decode("utf-8", errors="replace")
    finally:
        pass

# Processing function (per-script processing to keep memory bounded)
def process_one_script(script_name: str, script_id: str, uploaded_list) -> List[Tuple[str, bytes]]:
    """
    Transliterate all uploaded files into one script.
    Returns list of tuples (arcname, bytes_content) ready to put into zip.
    """
    results = []
    sanitized_folder = sanitize_filename(script_name)
    # Prepare list of texts
    tasks = []
    filenames = []
    for up in uploaded_list:
        # ensure file pointer at start
        try:
            up.seek(0)
        except Exception:
            pass
        text = read_file_content(up)
        tasks.append((text, script_id))
        filenames.append(up.name)

    # Use ProcessPoolExecutor with given worker count
    converted_texts = []
    # On some platforms setting start method helps (best effort)
    try:
        if hasattr(multiprocessing, "set_start_method"):
            multiprocessing.set_start_method("spawn", force=False)
    except Exception:
        # ignore if cannot set
        pass

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as exe:
        # map tasks; ensure order preserved
        for out in exe.map(transliterate_worker, tasks):
            converted_texts.append(out)

    # Build arcname/content list
    for fname, out_text in zip(filenames, converted_texts):
        arcname = f"{sanitized_folder}/{fname}"
        # encode as utf-8 bytes for zip
        b = out_text.encode("utf-8")
        results.append((arcname, b))
    return results

# Main conversion trigger
if start_btn:
    if not uploaded_files or len(uploaded_files) == 0:
        st.error("Please upload at least one .txt file (UTF-8).")
    else:
        if len(uploaded_files) > 200:
            st.warning("You uploaded more than 200 files; only the first 200 will be processed.")
            uploaded_files = uploaded_files[:200]

        # Prepare in-memory zip
        zip_buffer = io.BytesIO()
        total_scripts = len(SCRIPT_MAP) if convert_all else 1
        total_tasks = total_scripts * len(uploaded_files)
        progress_bar = st.progress(0)
        status_text = st.empty()
        bytes_written = 0

        # We'll write into the final ZIP as we go to save memory
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            script_iter = SCRIPT_MAP.items() if convert_all else [(single_target, SCRIPT_MAP[single_target])]

            script_count = 0
            processed = 0
            for script_name, script_id in script_iter:
                script_count += 1
                status_text.markdown(f"Transliterating to **{script_name}** ({script_id}) — script {script_count}/{total_scripts}")
                try:
                    per_script_results = process_one_script(script_name, script_id, uploaded_files)
                except Exception as e:
                    st.error(f"Error while processing script {script_name}: {e}")
                    # still continue to next script
                    per_script_results = []

                # write per-script files into zip
                for arcname, b in per_script_results:
                    zf.writestr(arcname, b)
                    processed += 1
                    # update progress
                    progress_bar.progress(int(processed / total_tasks * 100))

        zip_buffer.seek(0)
        st.success("Conversion complete — download ZIP below")
        st.download_button("Download transliterated ZIP", data=zip_buffer.getvalue(), file_name="transliterated_all_scripts.zip", mime="application/zip")
        # small memory hint
        st.info(f"Created ZIP approx size: {len(zip_buffer.getvalue())/1024:.1f} KB")
