import fitz


def load_pdf(path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        path: Path to the PDF file.

    Returns:
        Full extracted text from the PDF.
    """

    print(f"[PDF LOADER] Loading: {path}")

    try:
        document = fitz.open(path)

    except Exception as e:
        print(f"[PDF LOADER] Failed to open PDF: {e}")
        raise

    pages = []

    try:
        for page_number, page in enumerate(document):

            text = page.get_text()

            print(
                f"[PDF LOADER] Page {page_number + 1}: "
                f"{len(text)} characters"
            )

            if text.strip():
                pages.append(text)

    finally:
        document.close()

    full_text = "\n".join(pages)

    print(
        f"[PDF LOADER] Total characters: "
        f"{len(full_text)}"
    )

    return full_text