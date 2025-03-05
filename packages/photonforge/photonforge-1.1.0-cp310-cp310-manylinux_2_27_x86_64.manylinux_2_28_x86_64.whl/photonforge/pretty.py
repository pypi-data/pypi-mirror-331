from .extension import Component, Technology, LayerSpec

import html
from typing import Union


class _Tree:
    """Tree viewer for components.

    Create a tree view of the component dependency tree for console and
    notebook visualization.

    Args:
        component: Root component of the tree.
        by_reference: If ``True`` shows all references (with index) within
          a component. Otherwise, only shows unique dependencies.
        interactive: If ``True``, the notebook visualization will use
          interactive folds and includes SVG previews.
    """

    def __init__(
        self,
        component: Component,
        by_reference: bool = False,
        interactive: bool = False,
    ):
        self.component = component
        self.by_reference = by_reference
        self.interactive = interactive

    @staticmethod
    def _inner_tree(component: Component, prefix: str, index: str, by_reference: bool):
        result = [f"{prefix}{index}{component.name}"]
        if by_reference:
            dependencies = [reference.component for reference in component.references]
        else:
            dependencies = []
            for reference in component.references:
                ref_component = reference.component
                if ref_component not in dependencies:
                    dependencies.append(ref_component)

        ref_prefix = (
            "".join("│" if p == "│" or p == "├" else " " for p in prefix) + " " * len(index) + "├─"
        )
        n = len(dependencies)
        num_digits = len(str(n - 1))
        index = " "
        for i, dependency in enumerate(dependencies):
            if by_reference:
                index = "[" + str(i).rjust(num_digits) + "] "
            if i == n - 1:
                ref_prefix = ref_prefix[:-2] + "└─"
            result.extend(_Tree._inner_tree(dependency, ref_prefix, index, by_reference))
        return result

    def __repr__(self):
        return "\n".join(_Tree._inner_tree(self.component, "", "", self.by_reference))

    @staticmethod
    def _inner_html_tree(component: Component, prefix: str, index: str, by_reference: bool):
        result = [f'<span style="color:gray">{prefix}{index}</span>{component.name}<br>']
        if by_reference:
            dependencies = [reference.component for reference in component.references]
        else:
            dependencies = []
            for reference in component.references:
                ref_component = reference.component
                if ref_component not in dependencies:
                    dependencies.append(ref_component)

        ref_prefix = (
            "".join("│" if p == "│" or p == "├" else " " for p in prefix) + " " * len(index) + "├─"
        )
        n = len(dependencies)
        num_digits = len(str(n - 1))
        index = " "
        for i, dependency in enumerate(dependencies):
            if by_reference:
                index = "[" + str(i).rjust(num_digits, " ") + "] "
            if i == n - 1:
                ref_prefix = ref_prefix[:-2] + "└─"
            result.extend(_Tree._inner_html_tree(dependency, ref_prefix, index, by_reference))
        return result

    @staticmethod
    def _inner_interactive_html_tree(component: Component, index: int, by_reference: bool):
        if by_reference:
            dependencies = [reference.component for reference in component.references]
        else:
            dependencies = []
            for reference in component.references:
                ref_component = reference.component
                if ref_component not in dependencies:
                    dependencies.append(ref_component)

        margin = "1em" if index >= 0 else "0"
        details = "details open" if index < 0 else "details"
        title = f'<span style="color:black">{component.name}</span>'
        if by_reference and index >= 0:
            title = f'<spam style="font-family:monospace;color:gray">[{index}] </span>{title}'

        result = [
            f'<{details} style="border:1px solid #bdbdbd;border-radius:3px;margin-left:{margin}">'
            f'<summary style="padding:0.8ex;background-color:#f5f5f5;cursor:pointer">'
            f'{title}</summary><iframe style="border:0;width:100%;min-height:300px" '
            f'srcdoc="{html.escape(component._repr_svg_())}"></iframe>',
        ]
        for i, dependency in enumerate(dependencies):
            result.extend(_Tree._inner_interactive_html_tree(dependency, i, by_reference))
        result.append("</details>")

        return result

    def _repr_html_(self):
        if self.interactive:
            html = ["<div>"]
            html.extend(_Tree._inner_interactive_html_tree(self.component, -1, self.by_reference))
        else:
            html = ['<div style="font-family:monospace">']
            html.extend(_Tree._inner_html_tree(self.component, "", "", self.by_reference))
        html.append("</div>")
        return "".join(html)


class LayerTable(dict):
    """Layer specification table viewer.

    Create a table of layer specifications for console and notebook
    visualization.

    Args:
        obj: Technology instance or dictionary of layer specifications.
    """

    def __init__(self, obj: Union[Technology, dict[str, LayerSpec]]):
        if isinstance(obj, Technology):
            obj = obj.layers
        elif not isinstance(obj, dict) or not all(
            isinstance(k, str) and isinstance(v, LayerSpec) for k, v in obj.items()
        ):
            raise TypeError(
                "Expected a Technology instance or a dictionary of layer specifications."
            )
        super().__init__(obj)

    def _repr_html_(self):
        html = [
            "<table><thead><tr>"
            '<th style="text-align:center">Name</th>'
            '<th style="text-align:center">Layer</th>'
            '<th style="text-align:center">Description</th>'
            '<th style="text-align:center">Color</th>'
            '<th style="text-align:center">Pattern</th>'
            "</tr></thead><tbody>"
        ]
        for name, layer_spec in sorted(self.items()):
            color = "#" + "".join(f"{c:02x}" for c in layer_spec.color)
            html.append(
                "<tr>"
                f'<td style="text-align:left">{name}</td>'
                f'<td style="text-align:center">{layer_spec.layer}</td>'
                f'<td style="text-align:left">{layer_spec.description}</td>'
                f'<td style="text-align:center;background-color:{color[:7]}">{color}</td>'
                f'<td style="text-align:center">{layer_spec.pattern}</td>'
                "</tr>"
            )
        html.append("</tbody></table>")
        return "".join(html)

    def __repr__(self):
        data = sorted(self.items())
        titles = ["Name", "Layer", "Description", "Color", "Pattern"]
        columns = [
            [name for name, _ in data],
            [str(layer_spec.layer) for _, layer_spec in data],
            [layer_spec.description for _, layer_spec in data],
            ["#" + "".join(f"{c:02x}" for c in layer_spec.color) for _, layer_spec in data],
            [layer_spec.pattern for _, layer_spec in data],
        ]

        if len(data) > 0:
            lengths = [
                max(len(title), *(len(x) for x in column)) for title, column in zip(titles, columns)
            ]
        else:
            lengths = [len(title) for title in titles]

        for j, (column, w) in enumerate(zip(columns, lengths)):
            for i in range(len(data)):
                if j == 0 or j == 2:
                    column[i] = column[i].ljust(w)
                else:
                    column[i] = column[i].center(w)

        lines = [
            "  ".join(x.center(w) for x, w in zip(titles, lengths)),
            "-" * (sum(lengths) + (len(lengths) - 1) * 2),
            *("  ".join(column[i] for column in columns) for i in range(len(columns[0]))),
        ]
        return "\n".join(lines)
