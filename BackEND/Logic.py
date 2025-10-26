import re
import Web_Scraping as ws
import io
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import re

def display_course(course):
    return re.sub(r'^CAS', '', course, flags=re.IGNORECASE)


def normalize_separators(prereq_string):
    prereq_string = re.sub(r'\s*[,;]\s*', ' and ', prereq_string, flags=re.IGNORECASE)
    prereq_string = re.sub(r'(and\s+)+and', 'and', prereq_string, flags=re.IGNORECASE)
    prereq_string = re.sub(r'\s+', ' ', prereq_string)
    return prereq_string.strip()


def extract_prereqs(course_name):
    normalized_course = ws.normalize_course(course_name)
    if not normalized_course:
        return None

    description = ws.scrape_course_description(course_name)
    if not description:
        # course not available on BU site
        return "COURSE_NOT_FOUND"

    match = re.search(
        r'(?:Undergraduate\s+)?Prerequisite[s]?\s*:?\s*(.*?)(?=\s+-|$)',
        description,
        re.IGNORECASE | re.DOTALL
    )
    if not match:
        # course exists, but has no prereqs
        return ""

    prereq_text = match.group(1)
    prereq_text = ws.clean_text(prereq_text)   # keep your existing clean_text
    prereq_text = re.sub(r'\bCAS\s*', '', prereq_text, flags=re.IGNORECASE)
    prereq_text = clean_prereq_text(prereq_text)   # NEW STEP
    return prereq_text



def extract_course_codes(prereq_string):
    codes = re.findall(r'\b[A-Z]{2,4}\s*\d{3}[A-Z]?\b', prereq_string)
    slash_codes = re.findall(r'\b([A-Z]{2,4}\d{3})/([A-Z]{2,4}\d{3})\b', prereq_string)
    for c1, c2 in slash_codes:
        codes.append(c1)
        codes.append(c2)
    return list(set(codes))

def get_prereqs_for_courses(course_list, visited=None, level=0):
    if visited is None:
        visited = set()
    results = []
    indent = "    " * level

    for course in course_list:
        normalized_course = ws.normalize_course(course)
        if not normalized_course:
            results.append(f"{indent}{course} (cannot normalize)")
            continue

        if normalized_course in visited:
            continue
        visited.add(normalized_course)

        course_disp = display_course(normalized_course)
        prereq_string = extract_prereqs(course)

        if prereq_string == "COURSE_NOT_FOUND":
            # Skip unavailable courses
            continue

        if prereq_string:
            results.append(f"{indent}{course_disp} prerequisites: {prereq_string}")
            prereq_codes = extract_course_codes(prereq_string)
            if prereq_codes:
                results.extend(
                    get_prereqs_for_courses(prereq_codes, visited=visited, level=level + 1)
                )
        else:
            results.append(f"{indent}{course_disp} has no prerequisites")

    return results

def clean_prereq_text(prereq_text):
    # Remove parentheses
    prereq_text = re.sub(r'[\(\)]', '', prereq_text)

    # Remove "GRS" or "CAS" prefixes
    prereq_text = re.sub(r'\b(GRS|CAS)\s+', '', prereq_text, flags=re.IGNORECASE)

    # Replace slashes with "or"
    prereq_text = re.sub(r'\s*/\s*', ' or ', prereq_text)

    # Replace "&" with "and"
    prereq_text = re.sub(r'\s*&\s*', ' and ', prereq_text)

    # Handle "one of the following"
    prereq_text = re.sub(
        r'\bone of the following\b[:\-]?\s*',
        '',
        prereq_text,
        flags=re.IGNORECASE
    )
    # Turn comma-separated lists after “one of the following” into OR
    prereq_text = re.sub(r'(?<=following)([^.]*)', lambda m: m.group(1).replace(',', ' or '), prereq_text)

    # Normalize “and/or”
    prereq_text = re.sub(r'\band/or\b', 'or', prereq_text, flags=re.IGNORECASE)

    # Normalize separators
    prereq_text = re.sub(r'\s*[,;]\s*', ' and ', prereq_text)

    # Remove repeated “and” or “or”
    prereq_text = re.sub(r'\b(and|or)\s+\1\b', r'\1', prereq_text, flags=re.IGNORECASE)

    # Clean extra spaces
    prereq_text = re.sub(r'\s+', ' ', prereq_text).strip()

    return prereq_text

def classes_used(course_list):
    if isinstance(course_list, str):
        course_list = [course_list]
    return "\n".join(get_prereqs_for_courses(course_list))


def extract_hub(course_name):
    normalized_course = ws.normalize_course(course_name)
    if not normalized_course:
        return None

    description = ws.scrape_course_description(course_name)
    if not description:
        return "COURSE_NOT_FOUND"

    match = re.search(
        r"this course fulfills.*?BU Hub area[s]*:?\s*(.*?)\.",
        description,
        re.IGNORECASE | re.DOTALL
    )
    if not match:
        return ""

    hub_text = match.group(1)
    hub_text = ws.clean_text(hub_text)
    return hub_text.strip()


def get_hubs_for_courses(course_list, visited=None):
    if visited is None:
        visited = set()

    results = []

    for course in course_list:
        normalized_course = ws.normalize_course(course)
        if not normalized_course:
            results.append(f"{course} (cannot normalize)")
            continue

        if normalized_course in visited:
            continue
        visited.add(normalized_course)

        course_disp = re.sub(r'^CAS', '', normalized_course, flags=re.IGNORECASE)
        hub_text = extract_hub(course)

        if hub_text == "COURSE_NOT_FOUND":
            results.append(f"{course_disp}: Course not available")
        elif hub_text:
            results.append(f"{course_disp}: {hub_text}")
        else:
            results.append(f"{course_disp}: No Hub requirement")

    return "\n".join(results)


def hubs_used(course_list):
    if isinstance(course_list, str):
        course_list = [course_list]
    return get_hubs_for_courses(course_list)

def parse_prereq_logic(prereq_text):
    """
    Parse a prerequisite string into a nested structure of course codes with AND/OR relationships.
    Returns a nested dict/tuple representation.
    """
    prereq_text = clean_prereq_text(prereq_text)
    
    def parse(text):
        text = text.strip()
        # Handle parentheses recursively
        while '(' in text:
            text = re.sub(r'\(([^()]+)\)', lambda m: str(parse(m.group(1))), text)
        
        # Split AND/OR
        if ' and ' in text:
            parts = [p.strip() for p in re.split(r'\band\b', text)]
            return ('AND', [parse(p) for p in parts])
        elif ' or ' in text:
            parts = [p.strip() for p in re.split(r'\bor\b', text)]
            return ('OR', [parse(p) for p in parts])
        else:
            # Return normalized course code
            code_match = re.findall(r'\b[A-Z]{2,4}\s*\d{3}[A-Z]?\b', text)
            if code_match:
                return code_match if len(code_match) > 1 else code_match[0]
            return text

    return parse(prereq_text)


def extract_course_logic(course_name):
    """
    Return only the course codes and logical connections for a given course.
    """
    prereq_string = extract_prereqs(course_name)
    if not prereq_string:
        return None
    if prereq_string == "COURSE_NOT_FOUND":
        return f"{course_name} not found"
    
    return parse_prereq_logic(prereq_string)
 

def visualize_full_prereq_tree(course_name, save_path="prereq_tree.png"):
    import io
    import re
    import matplotlib.pyplot as plt
    import networkx as nx

    root = ws.normalize_course(course_name) or course_name
    prereq_string = extract_prereqs(root)

    # --- Handle missing or empty prerequisites ---
    if prereq_string == "COURSE_NOT_FOUND":
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, f"{display_course(root)}\nnot available",
                fontsize=14, ha='center', va='center', weight='bold')
        ax.set_axis_off()
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return save_path

    if not prereq_string:
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, f"{display_course(root)}\nhas no prerequisites",
                fontsize=14, ha='center', va='center', weight='bold')
        ax.set_axis_off()
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return save_path

    # --- Parse prerequisite string into structure ---
    def parse_prereq_text(text):
        text = text.strip()
        # Handle parentheses recursively
        while '(' in text:
            text = re.sub(r'\(([^()]+)\)', lambda m: parse_prereq_text(m.group(1)), text)
        # Detect AND/OR
        if ' and ' in text:
            parts = [p.strip() for p in re.split(r'\band\b', text)]
            return ('AND', [parse_prereq_text(p) for p in parts])
        elif ' or ' in text:
            parts = [p.strip() for p in re.split(r'\bor\b', text)]
            return ('OR', [parse_prereq_text(p) for p in parts])
        else:
            return ws.normalize_course(text) or text

    parsed = parse_prereq_text(prereq_string)

    # --- Build directed graph ---
    G = nx.DiGraph()
    visited = set()

    def add_structure(structure, parent):
        """Recursively add nodes with AND/OR logic."""
        if isinstance(structure, tuple):
            logic, items = structure
            logic_node = f"{logic}_{len(G.nodes())}"
            G.add_node(logic_node, label=logic)
            G.add_edge(logic_node, parent)
            for item in items:
                add_structure(item, logic_node)
        else:
            course = structure
            if course not in visited:
                visited.add(course)
                G.add_node(course, label=display_course(course))
            G.add_edge(course, parent)

    G.add_node(root, label=display_course(root))
    add_structure(parsed, root)

    # --- Compute custom layered layout (no Graphviz) ---
    # Reverse edges for top-down orientation
    revG = G.reverse(copy=False)
    depths = dict(nx.single_source_shortest_path_length(revG, root))
    levels = {}
    for n, d in depths.items():
        levels.setdefault(d, []).append(n)

    vertical_gap = 3.0
    horizontal_gap = 3.5
    pos = {}
    max_depth = max(levels.keys())

    for depth, nodes in sorted(levels.items()):
        nodes.sort()
        width = (len(nodes) - 1) * horizontal_gap
        x_start = -width / 2
        y = depth * vertical_gap
        for i, n in enumerate(nodes):
            pos[n] = (x_start + i * horizontal_gap, y)

    # --- Draw ---
    fig_h = (max_depth + 2) * vertical_gap
    fig_w = max(10, len(G.nodes()) * 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    node_labels = nx.get_node_attributes(G, 'label')
    node_colors = []
    for n in G.nodes():
        if n == root:
            node_colors.append('#7FB3D5')  # root
        elif 'AND' in n:
            node_colors.append('#F7DC6F')  # AND node
        elif 'OR' in n:
            node_colors.append('#F1948A')  # OR node
        else:
            node_colors.append('#A9DFBF')  # normal course

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2200,
                           edgecolors='black', linewidths=1.3, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=node_labels,
                            font_size=10, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=18,
                           width=1.4, edge_color='#444', ax=ax)

    # Flip Y so root is at top
    ax.set_ylim((max_depth + 1) * vertical_gap, -vertical_gap)
    ax.set_axis_off()
    ax.set_title(f"Full Prerequisite Tree for {display_course(root)}",
                 fontsize=16, pad=20)
    fig.tight_layout()

    fig.savefig(save_path, format='png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"✅ Prerequisite tree saved to {save_path}")
    return save_path


print(extract_course_logic("cs330"))
path = visualize_full_prereq_tree("cs330")
print("Saved tree at:", path)
