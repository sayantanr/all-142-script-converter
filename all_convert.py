import streamlit as st
import zipfile, os, io, requests
from aksharamukha import transliterate

# --- SCRIPT MAP (your full list should be inserted here) ---
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

# --- SAFE NAME FN ---
def sanitize(x):
    return ''.join(c for c in x if c.isalnum() or c in (' ','_','-')).replace(' ','_')

# --- TRANSLITERATION ---
def transliterate_text(text, src, tgt):
    try:
        return transliterate.process(src, tgt, text)
    except Exception:
        try:
            url = "https://aksharamukha-plugin.appspot.com/api/public"
            payload = {"source": src, "target": tgt, "text": text}
            r = requests.post(url, json=payload, timeout=20)
            if r.status_code == 200:
                return r.json().get("text", text)
        except:
            pass
    return text

# --- UI ---
st.title("ISO → Multi-Script Transliterater (200 Files)")

uploaded_files = st.file_uploader(
    "Upload up to 200 .txt files", type=["txt"], accept_multiple_files=True
)

convert_all = st.checkbox("Convert to ALL scripts at once (Option A: folder-wise)")

selected_script = None
if not convert_all:
    selected_script = st.selectbox("Choose target script", list(SCRIPT_MAP.keys()))

if st.button("Convert"):
    if not uploaded_files:
        st.error("Upload at least one file.")
    else:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:

            if convert_all:
                # --- MULTI-SCRIPT MODE ---
                for script_name, script_id in SCRIPT_MAP.items():
                    folder = sanitize(script_name)

                    for file in uploaded_files:
                        data = file.read().decode("utf-8")
                        converted = transliterate_text(data, "ISO", script_id)
                        arcname = f"{folder}/{file.name}"
                        z.writestr(arcname, converted)
                        file.seek(0)

            else:
                # --- SINGLE SCRIPT MODE ---
                script_id = SCRIPT_MAP[selected_script]
                folder = sanitize(selected_script)

                for file in uploaded_files:
                    data = file.read().decode("utf-8")
                    converted = transliterate_text(data, "ISO", script_id)
                    arcname = f"{folder}/{file.name}"
                    z.writestr(arcname, converted)
                    file.seek(0)

        st.download_button(
            label="Download ZIP", data=zip_buffer.getvalue(), file_name="transliterated_output.zip"
        )
