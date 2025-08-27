import os


def concatenate_files(output_filename="llms-full.txt"):
    """
    Concatenates the content of moviepy/README.md and all files under
    moviepy/docs into a single text file.
    """
    output_path = os.path.join(os.getcwd(), output_filename)
    readme_path = os.path.join(os.getcwd(), "README.md")
    docs_dir = os.path.join(os.getcwd(), "docs")

    all_content = []

    # Read README.md
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            all_content.append(f.read())
            all_content.append("\n\n--- END README.md ---\n\n")
    except FileNotFoundError:
        print(f"Error: {readme_path} not found.")
        return
    except Exception as e:
        print(f"Error reading {readme_path}: {e}")
        return

    binary_extensions = {'.jpeg', '.png', '.gif', '.mp4', '.zip', '.ico', '.svg'} # Added .ico and .svg as they are often binary or cause issues

    # Read all files in moviepy/docs recursively
    for root, _, files in os.walk(docs_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension in binary_extensions:
                print(f"Skipping binary file: {os.path.relpath(file_path, os.getcwd())}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    all_content.append(f"\n\n--- START {os.path.relpath(file_path, os.getcwd())} ---\n\n")
                    all_content.append(f.read())
                    all_content.append(f"\n\n--- END {os.path.relpath(file_path, os.getcwd())} ---\n\n")
            except UnicodeDecodeError:
                print(f"Skipping non-UTF-8 text file: {os.path.relpath(file_path, os.getcwd())}")
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

    # Write to the output file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("".join(all_content))
        print(f"Successfully concatenated content to {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")

if __name__ == "__main__":
    concatenate_files()
