import yaml


def load_yaml(file_path: str):
    """
    Load and parse a YAML file safely.

    Args:
        file_path (str): Path to YAML file

    Returns:
        dict: Parsed YAML content
    """

    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
            return data

    except FileNotFoundError:
        raise Exception("File not found. Please check the path.")

    except yaml.YAMLError as e:
        raise Exception(f"YAML parsing error: {e}")

    except Exception as e:
        raise Exception(f"Unexpected error: {e}")