#!/usr/bin/env python

import os.path
from pstats import Stats
import json

from jinja2 import Template

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from stats import table_rows, json_stats


def main():
    filename = r"//home//gpu2//Documents//snakeviz//hi.prof"
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        raise RuntimeError("the path %s does not exist" % filename)

    if not os.path.isdir(filename):
        try:
            open(filename)
        except IOError as e:
            raise RuntimeError(
                "the file %s could not be opened: %s" % (filename, str(e))
            )

        try:
            Stats(filename)
        except Exception:
            raise RuntimeError(
                ("The file %s is not a valid profile. " % filename)
                + "Generate profiles using: \n\n"
                "\tpython -m cProfile -o my_program.prof my_program.py\n\n"
                "Note that snakeviz must be run under the same "
                "version of Python as was used to create the profile.\n"
            )

    profile_name = filename
    abspath = os.path.abspath(profile_name)
    try:
        s = Stats(profile_name)
    except:
        raise RuntimeError("Could not read %s." % profile_name)

    # Load the Jinja2 template
    with open(r"/home/gpu2/Documents/snakeviz/snakeviz/templates/viz.html", "r") as f:
        template_content = f.read()
    template = Template(template_content)
    # Generate the table_rows and callees strings using the functions from the previous code
    table_rows_str = json.dumps(table_rows(s))
    callees_str = json.dumps(json_stats(s))

    # Render the template with the provided data
    html = template.render(
        profile_name=profile_name, table_rows=table_rows_str, callees=callees_str
    )

    # Write the rendered HTML to a new file
    with open(r"/home/gpu2/Documents/snakeviz/snakeviz/templates/viz2.html", "w") as f:
        f.write(html)

    # Open the rendered HTML file in a web browser
    import webbrowser

    webbrowser.open(
        "file://" + r"/home/gpu2/Documents/snakeviz/snakeviz/templates/viz2.html"
    )


if __name__ == "__main__":
    main()

#command to run simple http server
#python -m http.server 8080