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
    Parse prerequisites into nested AND/OR structure.
    Only keeps valid course codes like CS112.
    """
    prereq_text = clean_prereq_text(prereq_text)
    # Remove unwanted phrases
    prereq_text = re.sub(r'\bor equivalent\b', '', prereq_text, flags=re.IGNORECASE)
    prereq_text = re.sub(r'\bor consent of instructor\b', '', prereq_text, flags=re.IGNORECASE)

    def parse(text):
        text = text.strip()
        if not text:
            return None

        # Split AND first
        if ' and ' in text:
            parts = [parse(p) for p in re.split(r'\band\b', text)]
            parts = [p for p in parts if p]
            if not parts:
                return None
            return ('AND', parts)

        # Split OR next
        if ' or ' in text:
            parts = [parse(p) for p in re.split(r'\bor\b', text)]
            parts = [p for p in parts if p]
            if not parts:
                return None
            return ('OR', parts)

        # Only return valid course codes
        codes = re.findall(r'\b[A-Z]{2,4}\s*\d{3}[A-Z]?\b', text)
        if codes:
            return codes if len(codes) > 1 else codes[0]
        return None

    return parse(prereq_text)
def visualize_full_prereq_tree(course_name, return_buffer = False, save_path="../FrontEnd/src/prereq_tree.png"):
    import matplotlib.pyplot as plt
    import networkx as nx
    import io
    import os

    # Ensure save directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    root = ws.normalize_course(course_name.strip()) or course_name.strip()
    prereq_string = extract_prereqs(root)

    # --- Handle special cases first ---
    if prereq_string == "COURSE_NOT_FOUND" or not prereq_string:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_axis_off()
        if prereq_string == "COURSE_NOT_FOUND":
            ax.text(0.5, 0.5, f"{display_course(root)} is not available",
                    ha='center', va='center', fontsize=14, color='red', weight='bold')
        else:
            ax.text(0.5, 0.5, f"{display_course(root)} has no prerequisites",
                    ha='center', va='center', fontsize=14, color='blue', weight='bold')
        fig.tight_layout()
        fig.savefig(save_path, format='png', bbox_inches='tight', dpi=200)
        plt.close(fig)
        return save_path

    # --- Normal case ---
    G = nx.DiGraph()
    visited_courses = set()

    def add_structure(structure, parent=None):
        if structure is None:
            return

        if isinstance(structure, list):
            if len(structure) == 1:
                add_structure(structure[0], parent)
                return
            structure = ('OR', structure)

        if isinstance(structure, tuple):
            logic, items = structure
            if len(items) == 1:
                add_structure(items[0], parent)
                return
            logic_node = f"{logic}_{len(G.nodes())}"
            G.add_node(logic_node, label=logic)
            if parent:
                G.add_edge(parent, logic_node)
            for item in items:
                add_structure(item, logic_node)
            return

        course = structure
        if course in visited_courses:
            if parent:
                G.add_edge(parent, course)
            return
        visited_courses.add(course)
        G.add_node(course, label=display_course(course))
        if parent:
            G.add_edge(parent, course)

        prereq_str = extract_prereqs(course)
        if prereq_str and prereq_str != "COURSE_NOT_FOUND":
            logic_structure = parse_prereq_logic(prereq_str)
            if logic_structure:
                add_structure(logic_structure, course)

    add_structure(root)

    # --- Compute hierarchical positions ---
    def hierarchy_pos(G, root, vert_gap=3.0, x_min=0, x_max=1.0):
        pos = {}

        def subtree_width(node):
            children = list(G.successors(node))
            if not children:
                return 1
            return sum(subtree_width(c) for c in children)

        def _assign(node, x_left, x_right, depth=0):
            children = list(G.successors(node))
            pos[node] = ((x_left + x_right) / 2, -depth * vert_gap)
            if not children:
                return
            total = sum(subtree_width(c) for c in children)
            current_x = x_left
            for c in children:
                w = subtree_width(c)
                child_x_left = current_x
                child_x_right = current_x + (x_right - x_left) * (w / total)
                _assign(c, child_x_left, child_x_right, depth + 1)
                current_x += (x_right - x_left) * (w / total)

        _assign(root, x_min, x_max)
        return pos

    pos = hierarchy_pos(G, root)

    # --- Draw the graph ---
    fig_w = max(12, len(G.nodes()) * 1.2)
    fig_h = max(8, len(G.nodes()) * 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    node_labels = nx.get_node_attributes(G, 'label')
    node_colors, node_sizes = [], []
    for n in G.nodes():
        label = G.nodes[n]['label']
        if n == root:
            node_colors.append('#7FB3D5')
            node_sizes.append(2400)
        elif label == "AND":
            node_colors.append('#F7DC6F')
            node_sizes.append(1800)
        elif label == "OR":
            node_colors.append('#F1948A')
            node_sizes.append(1800)
        else:
            node_colors.append('#A9DFBF')
            node_sizes.append(2000)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           edgecolors='black', linewidths=1.3, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=18, width=1.4, edge_color='#444', ax=ax)

    ax.set_axis_off()
    ax.set_title(f"Full Prerequisite Tree with AND/OR for {display_course(root)}",
                 fontsize=16, pad=20)
    fig.tight_layout()

    # --- Save image ---
    if return_buffer:
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=200)
        img_buf.seek(0)
        plt.close(fig)
        return img_buf

    fig.savefig(save_path, format='png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    return save_path


# --- Example usage ---


