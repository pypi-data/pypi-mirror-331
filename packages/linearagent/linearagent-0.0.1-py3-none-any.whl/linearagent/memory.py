import json


class Memory:
    """
    A simple memory class to store and retrieve information.
    """

    def __init__(self):
        self.memory = {
            "thread": None,
        }  # General purpose memory store.

    def set(self, key: str, value):
        """
        Store a value in memory.
        Args:
            key (str): The key to store the value under.
            value: The value to store.
        """
        if key == "thread":
            raise ValueError("The 'thread' key is reserved.")
        if key == "all":
            raise ValueError("The 'all' key is reserved.")
        self.memory[key] = value

    def get(self, key: str):
        """
        Retrieve a value from memory.
        Args:
            key (str): The key to retrieve the value for.
        Returns:
            The value stored under the key.
        """
        if key == "all":
            return self
        return self.memory.get(key)

    def keys(self) -> list:
        """
        Retrieve a list of all keys in memory.
        Returns:
            list: A list of keys.
        """
        return self.memory.keys()

    def map_thread(self, existing_thread: dict):
        """
        Map an existing thread to the current thread.
        Args:
            existing_thread (dict): The existing thread to map.
        """
        self.memory["thread"] = existing_thread

    def _get_content_type(self, value):
        """
        Determine the content type of a value.
        Args:
            value: The value to determine the content type of.
        Returns:
            The content type of the value.
        """
        try:
            json.dumps(value)
            return "text"
        except (TypeError, ValueError):
            return "object"

    def stringify(self, include_thread=False) -> str:
        """
        Stringify the memory.
        Returns:
            str: A string representation of the memory.
        """
        lines = []
        lines.append("# --------------------------------")
        lines.append("Memory")
        lines.append("# --------------------------------")
        lines.append("")

        # Stringify each key-value pair, for all keys that can be stringified.
        for key, value in self.memory.items():
            if include_thread is False and key == "thread":
                continue  # Skip the thread key
            content_type = self._get_content_type(value)
            if content_type == "text":
                lines.append(f"Key: {key}")
                lines.append(f"Value: {value}")
                lines.append("")
            else:
                lines.append(f"Key: {key}")
                lines.append("Value: <object>")
                lines.append("")

        return "\n".join(lines)
