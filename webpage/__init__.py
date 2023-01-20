from pathlib import Path


def get_page() -> str:
    with open(Path(__file__).parent.joinpath('index.html')) as f:
        page = f.read()

    with open(Path(__file__).parent.joinpath('style.css')) as f:
        css = f.read()

    page = page.replace("/** THIS COMMENT WILL BE REPLACED BY CSS-STYLE **/", "<style>"+css+"</style>")

    return page