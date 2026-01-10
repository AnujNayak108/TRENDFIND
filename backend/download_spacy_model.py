"""
Wrapper script to download spaCy model with Python 3.12 compatibility fix
This must patch ForwardRef before any pydantic imports
"""
import sys

# CRITICAL: Patch must happen before ANY imports that might use pydantic
if sys.version_info >= (3, 12):
    import typing
    import inspect
    _original_evaluate = typing.ForwardRef._evaluate
    
    def _patched_evaluate(self, *args, **kwargs):
        """Patched version that handles both old (pydantic v1) and new (Python 3.12) signatures"""
        # Python 3.12 signature: _evaluate(self, globalns, localns, type_params, *, recursive_guard)
        # Pydantic v1 calls: _evaluate(globalns, localns, set()) - 3 positional args
        # We need to detect the old call pattern and convert it
        if len(args) == 3 and 'recursive_guard' not in kwargs:
            # Old pydantic v1 call pattern: (globalns, localns, frozenset)
            globalns, localns, recursive_guard = args
            return _original_evaluate(self, globalns, localns, type_params=None, recursive_guard=recursive_guard)
        elif len(args) == 2 and 'recursive_guard' not in kwargs:
            # Another possible pattern: (globalns, localns)
            globalns, localns = args
            return _original_evaluate(self, globalns, localns, type_params=None, recursive_guard=set())
        else:
            # New signature or already has recursive_guard
            if 'recursive_guard' not in kwargs:
                kwargs['recursive_guard'] = set()
            return _original_evaluate(self, *args, **kwargs)
    
    typing.ForwardRef._evaluate = _patched_evaluate

# Now import and run spacy download
if __name__ == "__main__":
    from spacy.cli import download
    
    # Download the model
    model_name = "en_core_web_sm" if len(sys.argv) == 1 else sys.argv[1]
    download(model_name)
