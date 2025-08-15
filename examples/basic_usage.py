"""Example usage of the database RAG system.

Enhancements:
- Falls back to the basic example automatically when running in a
    non-interactive environment (e.g., Docker ENTRYPOINT) to avoid EOFError.
- Allows forcing mode via EXAMPLE_MODE env var (values: 'basic',
    'interactive').
"""
import os
import sys
from dotenv import load_dotenv
from rag_system import create_system_from_env

# Ensure stdout/stderr use UTF-8 (some minimal containers default to ascii)
if hasattr(sys.stdout, "reconfigure"):
    try:  # noqa: SIM105
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

load_dotenv()


def basic_example():
    """Basic example showing automatic demonstrations"""
    print("=== INITIALIZING RAG SYSTEM ===")
    system = create_system_from_env()
    try:
        if not system.initialize():
            print("Failed to initialize the system!")
            return
        print("\n=== DATABASE INFORMATION ===")
        schema_info = system.get_schema_info()
        print(schema_info)
        print("\n=== AVAILABLE TABLES ===")
        tables = system.get_available_tables()
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        questions = [
            "How many tables exist in the database?",
            "What are the main relationships between the tables?",
            "Show a data example from the first table.",
            "Which columns are primary keys?",
            "Are there foreign keys? Which ones?",
        ]
        print("\n=== QUERY EXAMPLES ===")
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question}")
            print("-" * 50)
            result = system.ask(question)
            if result["status"] == "success":
                print(f"Answer: {result['sql_response']}")
                if result.get("relevant_context"):
                    print("\nRelevant retrieved context:")
                    for ctx in result["relevant_context"][:2]:
                        meta = ctx["metadata"]
                        print(f"  - Type: {meta.get('type', 'N/A')}")
                        if "table_name" in meta:
                            print(f"    Table: {meta['table_name']}")
            else:
                print(f"Error: {result['error']}")
        if tables:
            first = tables[0]
            print(f"\n=== TABLE PREVIEW: {first} ===")
            preview = system.get_table_preview(first, limit=5)
            if preview["status"] == "success":
                print(f"Columns: {', '.join(preview['columns'])}")
                print(f"Sample row count: {preview['row_count']}")
                print("\nData:")
                for i, row in enumerate(preview["data"], 1):
                    print(f"  Row {i}: {row}")
            else:
                print(f"Error retrieving preview: {preview['error']}")
    except Exception as e:  # noqa: BLE001
        print(f"Error during execution: {e}")
    finally:
        system.close()
        print("\n=== SYSTEM CLOSED ===")


def interactive_example():
    """Interactive example allowing user queries"""
    print("=== INTERACTIVE MODE ===")
    print("Type 'exit' to quit")
    system = create_system_from_env()
    try:
        if not system.initialize():
            print("Failed to initialize the system!")
            return
        print("\nSystem ready! You can ask questions about the database.")
        print("Examples:")
        print("- 'Which tables exist?'")
        print("- 'Show data from table X'")
        print("- 'How are the tables related?'")
        while True:
            try:
                question = input("\nYour question: ").strip()
            except EOFError:
                print("\nEOF detected. Exiting interactive mode.")
                break
            if question.lower() in ["sair", "quit", "exit"]:
                break
            if not question:
                continue
            result = system.ask(question)
            if result["status"] == "success":
                print(f"\nAnswer: {result['sql_response']}")
            else:
                print(f"\nError: {result['error']}")
    except KeyboardInterrupt:  # pragma: no cover
        print("\nInterrupted by user.")
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")
    finally:
        system.close()


if __name__ == "__main__":  # pragma: no cover
    required_vars = ["DATABASE_URL", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nConfigure these variables before running the program.")
        raise SystemExit(1)

    # Allow non-interactive selection
    forced_mode = os.getenv("EXAMPLE_MODE", "").strip().lower()
    if forced_mode in {"basic", "interactive"}:
        if forced_mode == "basic":
            basic_example()
        else:
            interactive_example()
        raise SystemExit(0)

    # If no TTY (e.g., Docker without interactive terminal) run basic
    if not sys.stdin.isatty():
        print(
            "[examples] No interactive TTY detected; running basic example by "
            "default."
        )
        basic_example()
        raise SystemExit(0)

    print("Choose the example type:")
    print("1. Basic example (automatic demonstrations)")
    print("2. Interactive example (you ask the questions)")
    try:
        try:
            choice = input("Type 1 or 2: ").strip()
        except EOFError:
            print(
                "\nEOF detected while reading choice; defaulting to basic "
                "example."
            )
            choice = "1"
        if choice == "1":
            basic_example()
        elif choice == "2":
            interactive_example()
        else:
            print("Invalid choice! Running basic example by default.")
            basic_example()
    except KeyboardInterrupt:  # pragma: no cover
        print("\nProgram interrupted.")
