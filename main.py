"""
RAG System for Databases - Main entry point
This file was refactored; functionality lives in modular files.
Use rag_system.py or examples.py for usage examples.
"""

from rag_system import create_system_from_env


def main():
    """Simple usage example of the refactored system"""
    print("=== RAG SYSTEM FOR DATABASES ===")
    print("This codebase was refactored for better organization.")
    print("See:")
    print("- rag_system.py: Main system")
    print("- examples.py: Complete examples")
    print("- README.md: Full documentation")
    print()

    try:
        system = create_system_from_env()

        if system.initialize():
            print("✓ System initialized successfully!")

            print("\n=== DATABASE INFO ===")
            tables = system.get_available_tables()
            print(f"Tables found: {len(tables)}")
            for table in tables[:5]:
                print(f"  - {table}")
            if len(tables) > 5:
                print(f"  ... and {len(tables) - 5} more tables")

            print("\n=== QUERY EXAMPLE ===")
            question = "What are the main tables of the system?"
            result = system.ask(question)
            if result["status"] == "success":
                print(f"Question: {question}")
                print(f"Answer: {result['sql_response']}")
            else:
                print(f"Query error: {result['error']}")
        else:
            print("✗ Failed to initialize system")
            print("Check your .env configuration")
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")
        print("\nTip: Run 'python examples.py' for complete examples")
    finally:
        if 'system' in locals():
            system.close()


if __name__ == "__main__":  # pragma: no cover
    main()
