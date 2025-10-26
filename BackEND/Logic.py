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
    # Remove parentheses entirely
    prereq_text = re.sub(r'[\(\)]', '', prereq_text)

    # Remove "GRS" prefix
    prereq_text = re.sub(r'\bGRS\s+', '', prereq_text, flags=re.IGNORECASE)

    # Replace slashes with " and "
    prereq_text = re.sub(r'\s*/\s*', ' and ', prereq_text)

    # Replace "&" with "and"
    prereq_text = re.sub(r'\s*&\s*', ' and ', prereq_text)

    # Normalize separators (commas, semicolons)
    prereq_text = re.sub(r'\s*[,;]\s*', ' and ', prereq_text)

    # Remove multiple spaces
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

def visualize_full_prereq_tree(course_name):
    import io
    import matplotlib.pyplot as plt
    import networkx as nx

    img_buf = io.BytesIO()
    root = ws.normalize_course(course_name) or course_name

    # Check if course exists or has prerequisites
    prereq_string = extract_prereqs(root)
    if prereq_string == "COURSE_NOT_FOUND":
        # Course not available → single node with message
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, f"Class {display_course(root)}\nis not available",
                fontsize=14, ha='center', va='center', weight='bold')
        ax.set_axis_off()
        fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
        plt.close(fig)
        img_buf.seek(0)
        return img_buf

    # Handle courses with no prerequisites
    if not prereq_string:
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(0.5, 0.5, f"{display_course(root)}\nhas no prerequisites",
                fontsize=14, ha='center', va='center', weight='bold')
        ax.set_axis_off()
        fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
        plt.close(fig)
        img_buf.seek(0)
        return img_buf

    # --------- Build the prerequisite tree --------- #
    G = nx.DiGraph()
    visited = set()
    prereq_cache = {}

    def add_course(course, parent=None):
        normalized = ws.normalize_course(course) or course
        if normalized in visited:
            if parent and not G.has_edge(normalized, parent):
                G.add_edge(normalized, parent)
            return
        visited.add(normalized)
        G.add_node(normalized)
        if parent:
            G.add_edge(normalized, parent)
        if normalized in prereq_cache:
            prereq_string = prereq_cache[normalized]
        else:
            prereq_string = extract_prereqs(normalized)
            prereq_cache[normalized] = prereq_string
        if not prereq_string or prereq_string == "COURSE_NOT_FOUND":
            return
        prereq_codes = extract_course_codes(prereq_string)
        for prereq in prereq_codes:
            add_course(prereq, parent=normalized)

    add_course(root)

    # --------- Layout nodes with equal vertical spacing --------- #
    depths = dict(nx.shortest_path_length(G.reverse(copy=False), source=root))
    levels = {}
    for node, d in depths.items():
        levels.setdefault(d, []).append(node)

    pos = {}
    vertical_gap = 3
    horizontal_gap = 4
    for d, nodes in levels.items():
        n_nodes = len(nodes)
        for i, node in enumerate(nodes):
            x = i * horizontal_gap
            y = -d * vertical_gap
            pos[node] = (x, y)

    # Node colors
    node_colors = []
    for n in G.nodes():
        if n == root:
            node_colors.append('#a6cee3')
        elif len(list(G.predecessors(n))) == 0:
            node_colors.append('#b2df8a')
        else:
            node_colors.append('#fdbf6f')
    node_sizes = [2000 for _ in G.nodes()]

    fig_width = max(12, max(len(nodes) for nodes in levels.values())*2)
    fig_height = max(6, (max(depths.values())+1)*vertical_gap)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(
        G, pos, arrows=True, arrowstyle='-|>', arrowsize=20,
        edge_color='gray', min_source_margin=15, min_target_margin=25
    )
    nx.draw_networkx_labels(G, pos, labels={n: display_course(n) for n in G.nodes()},
                            font_size=10, font_weight='bold')

    ax.set_axis_off()
    ax.set_title(f"Full Prerequisite Tree for {display_course(root)}", fontsize=16)

    fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    img_buf.seek(0)
    return img_buf
