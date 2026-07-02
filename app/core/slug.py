from slugify import slugify


def make_slug(name: str, number: int) -> str:
    """Слаг из названия (транслит кириллицы) и номера: «Футболка», 1 -> futbolka-1."""
    base = slugify(name) or "item"
    return f"{base}-{number}"
