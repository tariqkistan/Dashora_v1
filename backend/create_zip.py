import os
import zipfile
import sys
import shutil

def create_zip(source_dir, output_zip):
    """Create a zip file from a directory"""
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_zip)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if lambda_function.py exists
    lambda_function_path = os.path.join(source_dir, "lambda_function.py")
    if not os.path.exists(lambda_function_path):
        print(f"WARNING: lambda_function.py not found in {source_dir}")
        # Look for it in the current directory
        if os.path.exists("lambda_function.py"):
            print("Found lambda_function.py in current directory, copying to source directory")
            shutil.copy("lambda_function.py", lambda_function_path)
        else:
            print("ERROR: lambda_function.py not found!")
            return False
    
    # Create a new zip file
    print(f"Creating zip file: {output_zip}")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ensure lambda_function.py is added first
        print(f"Adding: lambda_function.py")
        zipf.write(lambda_function_path, "lambda_function.py")
        
        # Walk through all files and subdirectories
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # Skip lambda_function.py as we already added it
                if file == "lambda_function.py" and root == source_dir:
                    continue
                    
                file_path = os.path.join(root, file)
                # Calculate relative path for the archive
                rel_path = os.path.relpath(file_path, source_dir)
                print(f"Adding: {rel_path}")
                # Add file to the zip
                zipf.write(file_path, rel_path)
    
    print(f"Zip file created successfully: {output_zip}")
    print(f"Total size: {os.path.getsize(output_zip) / (1024 * 1024):.2f} MB")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_zip.py <source_dir> <output_zip>")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_zip = sys.argv[2]
    
    if not create_zip(source_dir, output_zip):
        sys.exit(1) 