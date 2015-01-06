from .action_history import ActionHistory


class PackagesLoader:

    """
    Load, store and install Javatar packages
    """

    @staticmethod
    def reset():
        ActionHistory.add_action(
            "javatar.core.packages_loader.reset", "Reset all packages"
        )
        PackagesLoader.packages = None

    @staticmethod
    def startup():
        ActionHistory.add_action(
            "javatar.core.packages_loader.startup", "Load packages"
        )

    @staticmethod
    def ready():
        return PackagesLoader.packages is not None
