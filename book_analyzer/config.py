"""
network.config
==============
Central visual configuration for the D3.js character network.
Edit colors, labels, and dash patterns here without touching rendering logic.
"""


class NetworkConfig:
    """Central place for all visual style constants used in the HTML output."""

    GROUP_COLORS = {
        "protagonist": "#c4a45a",
        "antagonist":  "#8b3333",
        "family":      "#4a7c9a",
        "ally":        "#3d7a52",
        "rival":       "#7a3d6b",
        "other":       "#6b6b6b",
    }

    LINK_COLORS = {
        "love":         "#c4905a",
        "family":       "#4a7c9a",
        "friendship":   "#3d7a52",
        "conflict":     "#8b3333",
        "rivalry":      "#7a3d6b",
        "professional": "#7a7a3d",
        "other":        "#5a6b5a",
    }

    GROUP_LABELS = {
        "protagonist": "Protagonist",
        "antagonist":  "Antagonist",
        "family":      "Family",
        "ally":        "Ally / Friend",
        "rival":       "Rival / Enemy",
        "other":       "Other",
    }

    # Relationship types that render as dashed lines
    LINK_DASH = {
        "professional": "5,3",
        "other":        "4,4",
    }

    DEFAULT_NODE_COLOR = "#6b6b6b"
    DEFAULT_LINK_COLOR = "#5a6b5a"
