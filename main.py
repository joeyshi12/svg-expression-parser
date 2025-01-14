import sys
import argparse
import xml.etree.ElementTree as ET
from svg.path import CubicBezier, Line, parse_path


def to_ellipse_expression(element: ET.Element) -> str:
    cx = element.get("cx")
    cy = element.get("cy")
    rx = element.get("rx")
    ry = element.get("ry")
    return f"\\left(\\frac{{x-{cx}}}{{{rx}}}\\right)^{{2}}+\\left(\\frac{{y-{cy}}}{{{ry}}}\\right)^{{2}}=1"


def to_path_expressions(element: ET.Element) -> list[str]:
    draw_path = element.get("d")
    if draw_path is None:
        return []

    expressions: list[str] = []
    for command in parse_path(draw_path):
        match command:
            case Line():
                x1, y1 = command.start.real, command.start.imag
                x2, y2 = command.end.real, command.end.imag
                if x1 != x2 or y1 != y2:
                    expressions.append(f"\\left([{x1},{y1}],[{x2},{y2}]\\right)")
            case CubicBezier():
                x1, y1 = command.start.real, command.start.imag
                x2, y2 = command.end.real, command.end.imag
                cx1, cy1 = command.control1.real, command.control1.imag
                cx2, cy2 = command.control2.real, command.control2.imag
                bx = f"(1-t)^{{3}}({x1})+3t(1-t)^{{2}}({cx1})+3t^{{2}}(1-t)({cx2})+t^{{3}}({x2})"
                by = f"(1-t)^{{3}}({y1})+3t(1-t)^{{2}}({cy1})+3t^{{2}}(1-t)({cy2})+t^{{3}}({y2})"
                expressions.append(f"({bx},{by})")
            case _:
                pass

    return expressions


def parse_expressions(element: ET.Element):
    if element.tag.endswith("ellipse"):
        print(to_ellipse_expression(element))
    elif element.tag.endswith("path"):
        for expression in to_path_expressions(element):
            print(expression)
    for child in element:
        parse_expressions(child)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("svg_file")
    args = parser.parse_args()

    if args.svg_file is None:
        sys.exit(1)

    tree = ET.parse(args.svg_file)
    root = tree.getroot()
    parse_expressions(root)


if __name__ == "__main__":
    main()
