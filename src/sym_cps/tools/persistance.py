# type: ignore
import os
import pickle

from sym_cps.shared.paths import persistence_path


def dump(obj: object, file: str) -> str:
    file_path = persistence_path / file

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "wb") as f:
        pickle.dump(obj=obj, file=f)
    print(f"Object saved in: {str(file_path)}")
    return str(file_path)


def load(file: str) -> object | None:
    file_path = persistence_path / file
    try:
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
        print(f"Object loaded from: {str(file_path)}")
        return obj
    except Exception:
        print(f"Exception while loading {file_path}")
        print(file)
        if "library" in file:
            from sym_cps.representation.library import Library
            print("returning empty library")
            return Library()
        if "designs" in file:
            print("returning empty dict")
            return dict()
        return None
