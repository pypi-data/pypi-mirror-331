from pathlib import Path
import yaml
from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type


class AuthorsPlugin(BasePlugin):
    config_scheme = (("authors_file", Type(str, default="authors.yaml")),)

    def __init__(self):
        self.authors = {}

    def on_config(self, config):
        """Load authors data from YAML file."""
        authors_file = self.config.get("authors_file")
        try:
            yaml_path = Path(config["docs_dir"]) / authors_file
            with yaml_path.open("r") as f:
                self.authors = yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Authors file '{authors_file}' not found.")
            self.authors = {}
        return config

    def on_page_markdown(self, markdown, page, config, files):
        """Process the markdown content to add author information."""
        # extract authors from the YAML front matter
        if page.meta and "authors" in page.meta:
            authors_list = page.meta["authors"]
            if not isinstance(authors_list, list):
                authors_list = [authors_list]

            # create HTML for author profiles at the bottom of the page
            html = "\n\n<hr><div class='authors-section'>\n"
            html += "<style>\n"
            html += "  .authors-list { display: flex; flex-wrap: wrap; gap: 10px; }\n"
            html += "  .author-card { display: flex; align-items: center; }\n"
            html += "  .author-image { width: 30px; height: 30px; border-radius: 50%; }\n"
            html += "</style>\n"
            html += "<div class='authors-list'>\n"

            for author_id in authors_list:
                if author_id in self.authors:
                    author = self.authors[author_id]
                    if "github" in author:
                        html += "<div class='author-card'>\n"
                        html += f"  <a href='https://github.com/{author['github']}' target='_blank'>\n"
                        html += f"    <img src='https://github.com/{author['github']}.png?size=30' alt='' class='author-image'>\n"
                        html += "  </a>\n"
                        html += "</div>\n"

            html += "</div>\n</div>"

            # append the HTML to the markdown content
            markdown += html

        return markdown
