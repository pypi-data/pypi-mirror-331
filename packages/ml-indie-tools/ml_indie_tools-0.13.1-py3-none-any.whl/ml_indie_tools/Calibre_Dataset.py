import logging
import os
from xml.etree import ElementTree as ET


class Calibre_Dataset:
    """A class to access and search text documents from a Calibre library.

    :param library_path: Path to the Calibre library
    """

    def __init__(self, library_path, verbose=True):
        self.log = logging.getLogger("CalibreLib")
        library_path = os.path.expanduser(library_path)
        if os.path.exists(os.path.join(library_path, "metadata.db")) is False:
            raise FileNotFoundError("Calibre library not found at " + library_path)

        self.library_path = library_path
        self.verbose = verbose
        self.records = []

    def load_index(self, use_aliases=False, max_file_size=None, truncate_large=True):
        """This function loads the Calibre library records that contain text-format books.

        :param use_aliases: If True, books are not referenced by title and author,
        :param max_file_size: If not None, files larger than max_file_size bytes are ignored or truncated (s.b.)
        :param truncate_large: On True, files larger than max_file_size are truncated instead of ignored, only if max_file_size is not None
        but by their numeric aliases, thus providing privacy.
        """
        # Enumerate all txt-format books
        self.records = []
        index = 1
        # Namespace map
        ns = {
            "opf": "http://www.idpf.org/2007/opf",
            "dc": "http://purl.org/dc/elements/1.1/",
        }
        for root, dirs, files in os.walk(self.library_path):
            for file in files:
                if file.endswith(".txt"):
                    opf_file = os.path.join(root, "metadata.opf")
                    if os.path.exists(opf_file):
                        try:
                            tree = ET.parse(opf_file)
                            title = tree.find(
                                ".//{http://purl.org/dc/elements/1.1/}title"
                            ).text
                            author = tree.find(
                                ".//{http://purl.org/dc/elements/1.1/}creator"
                            ).text
                            language = tree.find(
                                ".//{http://purl.org/dc/elements/1.1/}language"
                            ).text

                            # Dupe from Ebooks project, resolve at some point
                            metadata = tree.find("opf:metadata", ns)
                            subjects = metadata.findall("dc:subject", ns)
                            tags = [subject.text for subject in subjects]

                            uuid_element = tree.find(
                                './/dc:identifier[@opf:scheme="uuid"]',
                                namespaces={
                                    "opf": "http://www.idpf.org/2007/opf",
                                    "dc": "http://purl.org/dc/elements/1.1/",
                                },
                            )
                            if uuid_element is not None:
                                ebook_id = uuid_element.text
                            else:
                                self.log.error(
                                    f"Error parsing {opf_file}: No UUID found"
                                )
                                continue
                        except Exception as e:
                            self.log.error(f"Error parsing {opf_file}: {e}")
                            continue
                        filename = os.path.join(root, file)
                        rec = {
                            "ebook_id": ebook_id,
                            "author": author,
                            "language": language,
                            "title": title,
                            "filename": filename,
                            "tags": tags,
                        }
                        if use_aliases is True:
                            rec["alias"] = f"CL{index}"
                        with open(filename, "r", encoding="utf-8") as f:
                            rec["text"] = f.read()
                        if max_file_size is not None:
                            if len(rec["text"]) > max_file_size:
                                if truncate_large is True:
                                    rec["text"] = rec["text"][:max_file_size]
                                else:
                                    continue
                        self.records += [rec]
                        index += 1
        self.log.info(f"Loaded {len(self.records)} records from Calibre library.")
        return len(self.records)

    def search(self, search_dict):
        """Search for book record with key specific key values
        For a list of valid keys, use `get_record_keys()`
        Standard keys are: `ebook_id`, `author`, `language`, `title`, `tags`

        *Note:* :func:`~Calibre_Dataset.Calibre_Dataset.load_index` needs to be called once before this function can be used.

        Example: `search({"title": ["philosoph","phenomen","physic","hermeneu","logic"], "language":"english"})`
        Find all books whose titles contain at least one of the keywords, language english. Search keys can either be
        search for a single keyword (e.g. english), or an array of keywords.

        :returns: list of records"""
        if (
            not hasattr(self, "records")
            or self.records is None
            or len(self.records) == 0
        ):
            self.log.debug("Index not loaded, trying to load...")
            self.load_index()
        frecs = []
        for rec in self.records:
            found = True
            for sk in search_dict:
                if sk not in rec:
                    found = False
                    break
                else:
                    skl = search_dict[sk]
                    if not isinstance(skl, list):
                        skl = [skl]
                    nf = 0
                    for skli in skl:
                        skt = rec[sk]
                        if not isinstance(skt, list):
                            skt = [skt]
                        for sktj in skt:
                            if skli.lower() in sktj.lower():
                                nf = nf + 1
                    if nf == 0:
                        found = False
                        break
            if found is True:
                frecs += [rec]
        return frecs
