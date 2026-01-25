"""
Wrapper script to download spaCy model
"""
import sys

# Now import and run spacy download
if __name__ == "__main__":
    from spacy.cli import download
    
    # Download the model
    model_name = "en_core_web_sm" if len(sys.argv) == 1 else sys.argv[1]
    download(model_name)
