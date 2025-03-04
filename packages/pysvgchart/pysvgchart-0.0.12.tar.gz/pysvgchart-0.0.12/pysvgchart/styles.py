all_styles = {
    ".psc-hover-group text":
        {
            "display": "none;"
        },
    ".psc-hover-group:hover text":
        {
            "display": "inline"
        }
}

# .segment-area text {
#   display: none;
# }
#
# .segment-area:hover text {
#   display: inline;
# }
#
# .painted-area:hover .toggle-path {
#   opacity: 0.5;
# }
#
# svg path.toggle-path:hover {
#   opacity: 1.0 !important;
# }

def join_indent(values):
    return '\n'.join(['     ' + v for v in values])


def render_all_styles(styles=None):
    styles = all_styles if styles is None else styles
    return '\n'.join([
        '\n'.join([name + ' {', join_indent(s + ': ' + str(styles[name][s]) + ';' for s in styles[name]), '}\n'])
        for name in styles
    ])[:-1]
