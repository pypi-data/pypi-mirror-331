class RawRun:
    def __init__(self, text: str, color: str | None, highlight: str | None, style: str):
        self.text = text
        self.color = color
        self.highlight = highlight
        self.style = style

    def to_dict(self) -> dict:
        """Convert the instace to a dictionary representation"""
        return {
            "text": self.text,
            "color": self.color,
            "highlight": self.highlight,
            "style": self.style,
        }
