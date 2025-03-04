from docx.text.paragraph import Paragraph
from docx.styles.style import ParagraphStyle
from docx.text.run import Run
from .raw_logger import logger
from .raw_run import RawRun


def extract_runs(paragraph: Paragraph) -> list[dict]:
    if paragraph.text.startswith(
        "This template is intended for interventional clinical trials.  The template is suitable"
    ):
        logger.info(f"Paragraph style {paragraph.style.name}")
    data = [
        {
            "text": run.text,
            "color": _get_run_color(paragraph.style, run),
            "highlight": _get_highlight_color(run),
            "keep": True,
            # "style": run.style.name if run.style else paragraph.style.name
            "style": paragraph.style.name,
        }
        for run in paragraph.runs
    ]
    data = _tidy_runs_color(data)
    return [RawRun(x["text"], x["color"], x["highlight"], x["style"]) for x in data]


def _tidy_runs_color(data: list[dict]) -> list[dict]:
    more = False
    for index, run in enumerate(data):
        if (
            index > 0
            and run["color"] == data[index - 1]["color"]
            and run["highlight"] == data[index - 1]["highlight"]
        ):
            run["text"] = data[index - 1]["text"] + run["text"]
            data[index - 1]["keep"] = False
            more = True
    new_data = [x for x in data if x["keep"]]
    if more:
        new_data = _tidy_runs_color(new_data)
    return new_data


def _get_run_color(paragraph: Paragraph, run: Run) -> str | None:
    paragraph_color = _get_font_colour(paragraph)
    font_color = _get_font_colour(run)
    style_color = _run_style_color(run)
    if font_color:
        result = str(font_color)
    elif style_color:
        result = str(style_color)
    else:
        result = str(paragraph_color)
    return result


def _get_highlight_color(run: Run) -> str | None:
    try:
        return str(run.font.highlight_color)
    except Exception as e:
        logger.exception("Failed to get run highlight color", e)
        return None


def _run_style_color(run: Run) -> str | None:
    try:
        run_color = None
        run_style = run.style
        while run_style and not run_color:
            if run_style.font.color.rgb:
                run_color = run_style.font.color.rgb
            else:
                run_style = run_style.base_style
        return run_color
    except Exception as e:
        logger.exception("Failed to get run style color", e)
        return None


def _get_font_colour(item: Run | ParagraphStyle) -> str | None:
    try:
        return item.font.color.rgb
    except Exception as e:
        logger.exception("Failed to get font color", e)
        return None


setattr(Paragraph, "extract_runs", extract_runs)
