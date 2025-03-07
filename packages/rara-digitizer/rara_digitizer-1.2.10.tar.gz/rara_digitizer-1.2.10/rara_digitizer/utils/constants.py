# Most constants here are used as defaults for passable kwargs elsewhere.


# Defining known METS/ALTO section types that will be saved as separate document sections
LOOKUP_METSALTO_SECTIONS = [
    "article",
    # "section",
    "cover_section",
    "title_section",
    "bastard_title_section",
    "abstract",
    "poem",
    "preface",
    "postface",
    "table_of_contents",
    "indeks",
    "abbreviations",
    "introduction",
    "corrections",
    "list",
    "referencelist",
    "acknowledgements",
    "appendix",
    "dedication",
    "frontispiece",
    "bibliography",
    "advertisement",
    "obituary",
    "miscellaneous",
    "chapter",
]

# Defining known METS dmdSec ID's to look up document metadata
METS_META_IDS = ["MODSMD_PRINT", "MODSMD_ELEC", "MODSMD_ISSUE1", "MODS_ISSUE"]

# Defining METS fileGrp element patterns for looking up file group information
METS_FILEGROUP_PATTERNS = {
    "alto": ["alto", "text", "content"],
    "images": ["image", "img", "master"],
    "pdf": ["pdf"],
}
# Define all known METS/ALTO image labels
METSALTO_IMG_LABELS = [
    "illustration",
    "miscellaneous",
    "advertisement",
    "obituary",
    "table",
]

# Define which image labels will be kept as true labels for classification
KEEP_METSALTO_IMG_LABELS = {"obituary": "surmakuulutus", "table": "tabel"}

# Threshold of text quality, beneath which the text is considered to be of low quality and requires OCR
TEXT_QUALITY_THRESHOLD = 0.65
# Threshold of OCR confidence. OCR output with confidence below this threshold will be filtered out.
OCR_CONFIDENCE_THRESHOLD = 0.8 * 100
