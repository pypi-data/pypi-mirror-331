import os
import sys
import glob
import tempfile
from .conversation_analysis_processor import conv_analysis_processor

def get_input_directory():
    """Get input directory from environment variable or use default."""
    # Check for environment variable
    env_input_dir = os.environ.get('TherapeuticNLP_INPUT_DIR')
    if env_input_dir and os.path.exists(env_input_dir):
        return env_input_dir
    
    # Use default if environment variable is not set or directory doesn't exist
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_input_dir = os.path.join(parent_dir, "input_data")
    
    if env_input_dir and not os.path.exists(env_input_dir):
        print(f"Warning: Input directory from environment variable ({env_input_dir}) not found.")
        print(f"Falling back to default: {default_input_dir}")
    
    return default_input_dir

def get_output_directory():
    """Get output directory from environment variable or use default."""
    # Check for environment variable
    env_output_dir = os.environ.get('TherapeuticNLP_OUTPUT_DIR')
    if env_output_dir:
        # Create the directory if it doesn't exist
        os.makedirs(env_output_dir, exist_ok=True)
        return env_output_dir
    
    # Use default if environment variable is not set
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(parent_dir, "output_data")

def process_file(input_filepath):
    """Process a single transcript file and extract features."""
    
    # Check if file exists
    if not os.path.exists(input_filepath):
        print(f"Error: File {input_filepath} not found.")
        return
    
    # Get filename from path
    filename = os.path.basename(input_filepath)
    
    # Create output directory if it doesn't exist
    output_dir = get_output_directory()
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input file
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
    except Exception as e:
        print(f"Error reading file {input_filepath}: {e}")
        return
    
    # Extract features
    try:
        print(f"Extracting features from {filename}...")
        features = conv_analysis_processor(transcript_text, filename)
                
        print(f"Processing complete for {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")


def process_direct_input(transcript_text):
    """Process a transcript provided directly as text."""
    
    # Create a temporary file for the transcript
    try:
        # Create a temporary file with a meaningful name
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8') as temp:
            temp.write(transcript_text)
            temp_filepath = temp.name
        
        temp_filename = os.path.basename(temp_filepath)
        
        # Process the temporary file
        print(f"Processing direct input as temporary file: {temp_filename}")
        
        # Extract features
        features = conv_analysis_processor(transcript_text, "direct_input")
        
        print("Processing complete for direct input")
        
        # Clean up the temporary file
        os.unlink(temp_filepath)
        
    except Exception as e:
        print(f"Error processing direct input: {e}")


def get_direct_input():
    """Get transcript directly from user input."""
    print("\nEnter properly formatted chat transcript below.")
    print("Enter 'DONE' on a new line when finished:")
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'DONE':
            break
        lines.append(line)
    
    return '\n'.join(lines)


def get_input_files():
    """Interactive menu to select input files"""
    # Get input directory using environment variable or default
    input_dir = get_input_directory()
    
    # Check if input_data directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return []
    
    print(f"Using input directory: {input_dir}")
    
    # Get all text files in the input directory
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    all_files = []
    
    # Add other potential transcript files
    potential_files = glob.glob(os.path.join(input_dir, "*"))
    for file in potential_files:
        if os.path.isfile(file) and not file.endswith(".txt") and not file.endswith(".gitkeep") and not file.endswith(".py"):
            all_files.append(file)
    
    # Combine and sort all files
    all_files.extend(txt_files)
    all_files.sort()
    
    if not all_files:
        print("No input files found in the input directory.")
        return []
    
    # Display menu of available files
    print("\nAvailable transcript files:")
    for i, file in enumerate(all_files, 1):
        filename = os.path.basename(file)
        print(f"{i}. {filename}")
    
    print("\nOptions:")
    print("a. Process all files")
    print("b. Select specific files (comma-separated numbers)")
    print("c. Enter transcript directly")
    print("d. Quit")
    
    while True:
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == 'd':
            return []
        
        elif choice == 'a':
            print(f"Processing all {len(all_files)} files...")
            return all_files
        
        elif choice == 'b':
            try:
                selections = input("Enter file numbers (comma-separated): ").strip()
                indices = [int(x.strip()) - 1 for x in selections.split(',')]
                selected_files = [all_files[i] for i in indices if 0 <= i < len(all_files)]
                
                if not selected_files:
                    print("No valid files selected.")
                    continue
                
                print(f"Selected {len(selected_files)} files:")
                for file in selected_files:
                    print(f"- {os.path.basename(file)}")
                
                confirm = input("Proceed with these files? (y/n): ").strip().lower()
                if confirm == 'y':
                    return selected_files
                else:
                    print("Selection cancelled.")
            except (ValueError, IndexError) as e:
                print(f"Invalid selection: {e}")
        
        elif choice == 'c':
            transcript_text = get_direct_input()
            if transcript_text.strip():
                process_direct_input(transcript_text)
                return []  # Return empty list as we've already processed the input
            else:
                print("No transcript provided. Please try again.")
        
        else:
            print("Invalid option, please try again.")


def main():
    """Main function to run feature extraction on input files."""
    
    print("=" * 60)
    print("Conversation Analysis Feature Extraction Tool")
    print("=" * 60)
    
    # Show directory settings
    input_dir = get_input_directory()
    output_dir = get_output_directory()
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # If command line arguments are provided, use those
    if len(sys.argv) > 1:
        print("Using files specified in command line arguments...")
        for filepath in sys.argv[1:]:
            process_file(filepath)
        return
    
    # Otherwise, use interactive mode
    files_to_process = get_input_files()
    
    if not files_to_process:
        print("No files selected for processing. Exiting.")
        return
    
    # Process each file
    print("\nStarting feature extraction...")
    for i, filepath in enumerate(files_to_process, 1):
        print(f"\nFile {i} of {len(files_to_process)}")
        process_file(filepath)
    
    print("\nAll processing complete!")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()