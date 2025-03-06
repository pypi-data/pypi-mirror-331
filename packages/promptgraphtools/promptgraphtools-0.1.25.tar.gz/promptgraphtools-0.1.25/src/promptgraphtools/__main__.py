import argparse

from .code_autogen.graph_generator import generate_graph_code
from .code_autogen.schema_io import prune_unused_files

def main():
    parser = argparse.ArgumentParser(description="Generate Python code for StepGraph or prune unused files.")
    subparsers = parser.add_subparsers(dest='command', help='Commands')


    generate_parser = subparsers.add_parser('generate', help='Generate code from schema')
    prune_parser = subparsers.add_parser('prune', help='Prune unused function and template files')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(1)

    if args.command == 'generate':
        try:
            generate_graph_code()
            print("Code generated successfully.")
        except Exception as e:
            print(f"Error during code generation: {e}")
            exit(1)
    elif args.command == 'prune':
        prune_unused_files()
        print("Pruning completed.")


if __name__ == "__main__":
    main()
