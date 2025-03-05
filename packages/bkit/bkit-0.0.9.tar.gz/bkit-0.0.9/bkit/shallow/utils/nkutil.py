class HParams:
    """
    A class to manage hyperparameters and their settings.

    This class provides methods for setting, retrieving, and printing hyperparameters.
    """

    _skip_keys = ["populate_arguments", "set_from_args", "print", "to_dict"]

    def __init__(self, **kwargs):
        """
        Initialize the HParams instance with provided hyperparameters.

        Args:
            **kwargs: Hyperparameters and their values.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        """
        Get the value of a hyperparameter using dictionary-like syntax.

        Args:
            item (str): The name of the hyperparameter.

        Returns:
            Any: The value of the hyperparameter.
        """
        return getattr(self, item)

    def __setitem__(self, item, value):
        """
        Set the value of a hyperparameter using dictionary-like syntax.

        Args:
            item (str): The name of the hyperparameter.
            value (Any): The new value for the hyperparameter.

        Raises:
            KeyError: If the hyperparameter has not been declared yet.
        """
        if not hasattr(self, item):
            raise KeyError(f"Hyperparameter {item} has not been declared yet")
        setattr(self, item, value)

    def to_dict(self):
        """
        Convert the hyperparameters to a dictionary.

        Returns:
            dict: A dictionary containing hyperparameter names and values.
        """
        res = {}
        for k in dir(self):
            if k.startswith("_") or k in self._skip_keys:
                continue
            res[k] = self[k]
        return res

    def populate_arguments(self, parser):
        """
        Add hyperparameters as command-line arguments to an ArgumentParser.

        Args:
            parser (ArgumentParser): The ArgumentParser instance to add arguments to.
        """
        for k in dir(self):
            if k.startswith("_") or k in self._skip_keys:
                continue
            v = self[k]
            k = k.replace("_", "-")
            if type(v) in (int, float, str):
                parser.add_argument(f"--{k}", type=type(v), default=v)
            elif isinstance(v, bool):
                if not v:
                    parser.add_argument(f"--{k}", action="store_true")
                else:
                    parser.add_argument(f"--no-{k}", action="store_false")

    def set_from_args(self, args):
        """
        Set hyperparameters from command-line arguments.

        Args:
            args: The parsed command-line arguments.
        """
        for k in dir(self):
            if k.startswith("_") or k in self._skip_keys:
                continue
            if hasattr(args, k):
                self[k] = getattr(args, k)
            elif hasattr(args, f"no_{k}"):
                self[k] = getattr(args, f"no_{k}")

    def print(self):
        """
        Print the hyperparameters and their values.

        Returns:
            str: A string representation of hyperparameter names and values.
        """
        p_str = ""
        for k in dir(self):
            if k.startswith("_") or k in self._skip_keys:
                continue
            # print(k, repr(self[k]))
            p_str += str(k) + "\t" + str(repr(self[k])) + "\n"
        return p_str
