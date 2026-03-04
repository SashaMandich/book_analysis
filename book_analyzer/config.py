"""
network.config
==============
Central visual configuration for the D3.js character network.
Edit colors, labels, and dash patterns here without touching rendering logic.
"""


class NetworkConfig:
    """Central place for all visual style constants used in the HTML output."""

    GROUP_COLORS = {
        "protagonist": "#c49a50",
        "antagonist":  "#c47070",
        "family":      "#6a9ab8",
        "ally":        "#6aaa7a",
        "rival":       "#a87aaa",
        "other":       "#8a9aaa",
    }

    LINK_COLORS = {
        "love":         "#d4906a",
        "family":       "#6a9ab8",
        "friendship":   "#6aaa7a",
        "conflict":     "#c47070",
        "rivalry":      "#a87aaa",
        "professional": "#a0a870",
        "other":        "#8a9aaa",
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

    DEFAULT_NODE_COLOR = "#8a9aaa"
    DEFAULT_LINK_COLOR = "#8a9aaa"
