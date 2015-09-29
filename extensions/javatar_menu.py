from ..core import (
    DependencyManager,
    SnippetsManager,
    StateProperty
)
from ..utils import (
    Constant
)
from Javatar.api import *


class JavatarMenu(JavatarPlugin):
    def on_presetup_menu(self):
        DependencyManager().refresh_dependencies()
        StateProperty().refresh_library_paths()
        StateProperty().refresh_source_folders()

    def on_setup_menu(self, menu):
        # Create a menu for development channel
        if Constant.is_debug():
            menu.add_item(
                "main",
                ["Development Section...", "All testing tools"],
                {"name": "dev"},
                -1
            )

        # Generate action for Create menu
        actions = []
        for snippet in SnippetsManager().get_snippet_info_list():
            actions += [
                {
                    "command": "javatar_create",
                    "args": {"create_type": snippet[0]}
                }
            ]
        menu.add_items(
            "creates",
            SnippetsManager().get_snippet_info_list(),
            actions
        )
        menu.set_selected_index("creates", 3 if len(actions) > 0 else 2)

        # Quick reload menu
        if Constant.is_debug():
            menu.add_item(
                "main",
                ["Reload Javatar", "Reload Javatar modules (debug only)"],
                {
                    "command": "javatar_utils",
                    "args": {"util_type": "reload"}
                },
                0
            )

        # Show version on help menu
        menu.add_item(
            "help",
            ["Javatar", "v" + Constant.get_version()],
            {}
        )
