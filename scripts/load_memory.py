from ingestion.loader import load_semantic_memory


def main():

    pdf_path = (
        "data/semantic_memory_example.pdf"
    )

    user_id = "user_001"

    result = load_semantic_memory(
        pdf_path=pdf_path,
        user_id=user_id,
    )

    print(
        "\nFINAL RESULT:"
    )

    print(result)


if __name__ == "__main__":
    main()