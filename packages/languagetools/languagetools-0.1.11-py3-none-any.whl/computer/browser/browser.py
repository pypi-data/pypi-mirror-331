# from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import time
from sys import platform
import subprocess
import requests
import os
import logging
import random
from .advanced import advanced_browser

black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "script", "style", "path", "svg", "br", "::marker",])

class Browser:
    def __init__(self, computer, headless=False, viewport={"width": 1280, "height": 720}):
        self.computer = computer
        self.headless = headless
        self.viewport = viewport
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.page_element_buffer = {}
        
        # Set up logging
        # logging.basicConfig(level=logging.INFO)
        # self.logger = logging.getLogger(__name__)

    def search(self, query):
        """
        Searches the web for the specified query and returns the results.
        """
        headers = {"Authorization": f"Bearer {self.computer.api_key}"}
        response = requests.post(
            f'{self.computer.api_base}/tools/',
            json={"tool": "search", "input": {"query": query}},
            headers=headers
        )
        return response.json()["output"]

    def advanced_request(self, task):
        """
        Operates a browser to accomplish the task.
        """
        return advanced_browser(task, self.computer.api_key, self.computer.api_base+"/openai")
        
class ExtendedBrowser(Browser):
    async def start(self):
        self.playwright = await async_playwright().start()

        try:
            # Try to find Chrome profile
            chrome_profile_path = None
            if platform == "darwin":  # MacOS
                chrome_profile_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
            elif platform == "win32":  # Windows
                chrome_profile_path = os.path.join(os.environ["LOCALAPPDATA"], "Google/Chrome/User Data")
            elif platform == "linux":  # Linux
                chrome_profile_path = os.path.expanduser("~/.config/google-chrome")

            default_profile_path = os.path.join(chrome_profile_path, "Default") if chrome_profile_path else None
            
            try:
                if default_profile_path and os.path.exists(default_profile_path):
                    self.logger.info(f"Attempting to use Chrome profile at: {chrome_profile_path}")
                    self.browser = await self.playwright.chromium.launch_persistent_context(
                        user_data_dir=chrome_profile_path,
                        headless=self.headless,
                        viewport=self.viewport,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-blink-features=AutomationControlled",
                        ],
                        user_agent=f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(10,15)}_{random.randint(1,7)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(80,110)}.0.{random.randint(1000,5000)}.{random.randint(10,500)} Safari/537.36"
                    )
                    self.context = self.browser
                    self.page = await self.context.new_page()
                    return self
                else:
                    raise FileNotFoundError("No Chrome profile found")
                
            except Exception as profile_error:
                self.logger.warning(f"Failed to use Chrome profile: {str(profile_error)}")
                self.logger.info("Falling back to clean browser instance")
                # Fall back to regular browser launch
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                self.context = await self.browser.new_context(
                    viewport=self.viewport,
                    ignore_https_errors=True
                )
                self.page = await self.context.new_page()
                
        except Exception as e:
            self.logger.error(f"Error launching browser: {str(e)}")
            # Install Chromium browser binaries using subprocess
            self.logger.info("Attempting to install Chromium...")
            subprocess.run(["playwright", "install", "chromium"], check=True)
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport=self.viewport,
                ignore_https_errors=True
            )
            self.page = await self.context.new_page()

        return self

    async def stop(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def go_to_page(self, url, timeout=60000):
        await self.page.goto(url=url if "://" in url else "http://" + url, timeout=timeout)
        self.client = await self.page.context.new_cdp_session(self.page)
        self.page_element_buffer = {}

    async def read(self):
        # Wait for the page to finish loading
        # await self.page.wait_for_load_state("networkidle")
        # await self.page.wait_for_load_state("networkidle2")
        time.sleep(2)
        elements = await self.crawl()
        print("\n".join(elements))
        print("These IDs are programatically generated, so standard playwright clicks wont work. To click these elements, you MUST use the specialized tool `computer.browser.click(element_id)`.")

    async def crawl(self):
        page = self.page
        self.page_element_buffer = {}
        start = time.time()

        page_state_as_text = []

        device_pixel_ratio = await page.evaluate("window.devicePixelRatio")
        if platform == "darwin" and device_pixel_ratio == 1:  # lies
            device_pixel_ratio = 2

        win_scroll_x         = await page.evaluate("window.scrollX")
        win_scroll_y         = await page.evaluate("window.scrollY")
        win_upper_bound     = await page.evaluate("window.pageYOffset")
        win_left_bound         = await page.evaluate("window.pageXOffset") 
        win_width             = await page.evaluate("window.screen.width")
        win_height             = await page.evaluate("window.screen.height")
        win_right_bound     = win_left_bound + win_width
        win_lower_bound     = win_upper_bound + win_height
        document_offset_height = await page.evaluate("document.body.offsetHeight")
        document_scroll_height = await page.evaluate("document.body.scrollHeight")

#        percentage_progress_start = (win_upper_bound / document_scroll_height) * 100
#        percentage_progress_end = (
#            (win_height + win_upper_bound) / document_scroll_height
#        ) * 100
        percentage_progress_start = 1
        percentage_progress_end = 2

        page_state_as_text.append(
            {
                "x": 0,
                "y": 0,
                "text": "[scrollbar {:0.2f}-{:0.2f}%]".format(
                    round(percentage_progress_start, 2), round(percentage_progress_end)
                ),
            }
        )

        tree = await self.client.send(
            "DOMSnapshot.captureSnapshot",
            {"computedStyles": [], "includeDOMRects": True, "includePaintOrder": True},
        )
        strings         = tree["strings"]
        document     = tree["documents"][0]
        nodes         = document["nodes"]
        backend_node_id = nodes["backendNodeId"]
        attributes     = nodes["attributes"]
        node_value     = nodes["nodeValue"]
        parent         = nodes["parentIndex"]
        node_types     = nodes["nodeType"]
        node_names     = nodes["nodeName"]
        is_clickable = set(nodes["isClickable"]["index"])

        text_value             = nodes["textValue"]
        text_value_index     = text_value["index"]
        text_value_values     = text_value["value"]

        input_value         = nodes["inputValue"]
        input_value_index     = input_value["index"]
        input_value_values     = input_value["value"]

        input_checked         = nodes["inputChecked"]
        layout                 = document["layout"]
        layout_node_index     = layout["nodeIndex"]
        bounds                 = layout["bounds"]

        cursor = 0
        html_elements_text = []

        child_nodes = {}
        elements_in_view_port = []

        anchor_ancestry = {"-1": (False, None)}
        button_ancestry = {"-1": (False, None)}

        def convert_name(node_name, has_click_handler, element_attributes):
            role = element_attributes.get("role", "").lower()
            if node_name == "a":
                return "link"
            if node_name in ["input", "textarea"] or role == "textbox":
                return "textarea" if node_name == "textarea" or role == "textbox" else "input"
            if node_name == "img":
                return "img"
            if node_name == "button" or has_click_handler or role == "button":
                return "button"
            else:
                return "text"

        def find_attributes(attributes, keys):
            values = {}

            for [key_index, value_index] in zip(*(iter(attributes),) * 2):
                if value_index < 0:
                    continue
                key = strings[key_index]
                value = strings[value_index]

                if key in keys:
                    values[key] = value
                    keys.remove(key)

                    if not keys:
                        return values

            return values

        def add_to_hash_tree(hash_tree, tag, node_id, node_name, parent_id):
            parent_id_str = str(parent_id)
            if not parent_id_str in hash_tree:
                parent_name = strings[node_names[parent_id]].lower()
                grand_parent_id = parent[parent_id]

                add_to_hash_tree(
                    hash_tree, tag, parent_id, parent_name, grand_parent_id
                )

            is_parent_desc_anchor, anchor_id = hash_tree[parent_id_str]

            # even if the anchor is nested in another anchor, we set the "root" for all descendants to be ::Self
            if node_name == tag:
                value = (True, node_id)
            elif (
                is_parent_desc_anchor
            ):  # reuse the parent's anchor_id (which could be much higher in the tree)
                value = (True, anchor_id)
            else:
                value = (
                    False,
                    None,
                )  # not a descendant of an anchor, most likely it will become text, an interactive element or discarded

            hash_tree[str(node_id)] = value

            return value

        async def get_dropdown_options(element):
            options = await self.page.evaluate("""(element) => {
                if (!element) return null;
                if (element.tagName && element.tagName.toLowerCase() === 'select') {
                    return Array.from(element.options).map(option => ({
                        value: option.value,
                        text: option.text,
                        selected: option.selected
                    }));
                } else if (element.getAttribute && element.getAttribute('role') === 'listbox') {
                    return Array.from(element.querySelectorAll('[role="option"]')).map(option => ({
                        value: option.getAttribute('data-value') || option.id,
                        text: option.textContent,
                        selected: option.getAttribute('aria-selected') === 'true'
                    }));
                }
                return null;
            }""", element)
            return options

        for index, node_name_index in enumerate(node_names):
            node_parent = parent[index]
            node_name = strings[node_name_index].lower()

            is_ancestor_of_anchor, anchor_id = add_to_hash_tree(
                anchor_ancestry, "a", index, node_name, node_parent
            )

            is_ancestor_of_button, button_id = add_to_hash_tree(
                button_ancestry, "button", index, node_name, node_parent
            )

            try:
                cursor = layout_node_index.index(
                    index
                )  # todo replace this with proper cursoring, ignoring the fact this is O(n^2) for the moment
            except:
                continue

            if node_name in black_listed_elements:
                continue

            [x, y, width, height] = bounds[cursor]
            x /= device_pixel_ratio
            y /= device_pixel_ratio
            width /= device_pixel_ratio
            height /= device_pixel_ratio

            elem_left_bound = x
            elem_top_bound = y
            elem_right_bound = x + width
            elem_lower_bound = y + height

            partially_is_in_viewport = (
                elem_left_bound < win_right_bound
                and elem_right_bound >= win_left_bound
                and elem_top_bound < win_lower_bound
                and elem_lower_bound >= win_upper_bound
            )

            if not partially_is_in_viewport:
                continue

            meta_data = []

            # inefficient to grab the same set of keys for kinds of objects but its fine for now
            element_attributes = find_attributes(
                attributes[index], ["type", "placeholder", "aria-label", "title", "alt", "role"]
            )

            ancestor_exception = is_ancestor_of_anchor or is_ancestor_of_button
            ancestor_node_key = (
                None
                if not ancestor_exception
                else str(anchor_id)
                if is_ancestor_of_anchor
                else str(button_id)
            )
            ancestor_node = (
                None
                if not ancestor_exception
                else child_nodes.setdefault(str(ancestor_node_key), [])
            )

            if node_name == "#text" and ancestor_exception:
                text = strings[node_value[index]]
                if text == "|" or text == "•":
                    continue
                ancestor_node.append({
                    "type": "type", "value": text
                })
            else:
                if (
                    node_name == "input" and element_attributes.get("type") == "submit"
                ) or node_name == "button" or element_attributes.get("role") == "button":
                    node_name = "button"
                    element_attributes.pop(
                        "type", None
                    )  # prevent [button ... (button)..]
                
                for key in element_attributes:
                    if ancestor_exception:
                        ancestor_node.append({
                            "type": "attribute",
                            "key":  key,
                            "value": element_attributes[key]
                        })
                    else:
                        meta_data.append(f'{key}="{element_attributes[key]}"')

            element_node_value = None

            if node_value[index] >= 0:
                element_node_value = strings[node_value[index]]
                if element_node_value == "|": #commonly used as a seperator, does not add much context - lets save ourselves some token space
                    continue
            elif (
                node_name == "input"
                and index in input_value_index
                and element_node_value is None
            ):
                node_input_text_index = input_value_index.index(index)
                text_index = input_value_values[node_input_text_index]
                if node_input_text_index >= 0 and text_index >= 0:
                    element_node_value = strings[text_index]

            # remove redudant elements
            if ancestor_exception and (node_name != "a" and node_name != "button"):
                continue

            elements_in_view_port.append(
                {
                    "node_index": str(index),
                    "backend_node_id": backend_node_id[index],
                    "node_name": node_name,
                    "node_value": element_node_value,
                    "node_meta": meta_data,
                    "is_clickable": index in is_clickable,
                    "origin_x": int(x),
                    "origin_y": int(y),
                    "center_x": int(x + (width / 2)),
                    "center_y": int(y + (height / 2)),
                }
            )

        # lets filter further to remove anything that does not hold any text nor has click handlers + merge text from leaf#text nodes with the parent
        elements_of_interest= []
        id_counter = 0

        for element in elements_in_view_port:
            node_index = element.get("node_index")
            node_name = element.get("node_name")
            node_value = element.get("node_value")
            is_clickable = element.get("is_clickable")
            origin_x = element.get("origin_x")
            origin_y = element.get("origin_y")
            center_x = element.get("center_x")
            center_y = element.get("center_y")
            meta_data = element.get("node_meta")

            inner_text = ""
            placeholder = ""
            
            if node_name in ["input", "textarea"] or "role=\"textbox\"" in meta_data:
                placeholder = next((attr.split('=')[1].strip('"') for attr in meta_data if attr.startswith("placeholder")), "")
                inner_text = node_value if node_value else ""
            else:
                inner_text = f"{node_value} " if node_value else ""
            
            meta = ""
            
            if node_index in child_nodes:
                for child in child_nodes.get(node_index):
                    entry_type = child.get('type')
                    entry_value= child.get('value')

                    if entry_type == "attribute":
                        entry_key = child.get('key')
                        if entry_key == "placeholder":
                            placeholder = entry_value
                        else:
                            meta_data.append(f'{entry_key}="{entry_value}"')
                    elif node_name not in ["input", "textarea"] and "role=\"textbox\"" not in meta_data:
                        inner_text += f"{entry_value} "

            if meta_data:
                meta_string = " ".join(meta_data)
                meta = f" {meta_string}"

            if inner_text != "":
                inner_text = f"{inner_text.strip()}"

            converted_node_name = convert_name(node_name, is_clickable, dict(attr.split('=') for attr in meta_data))

            # Check if the element is a dropdown
            is_dropdown = node_name == 'select' or (node_name == 'div' and 'role="listbox"' in meta)
            
            if is_dropdown:
                dropdown_options = await get_dropdown_options(element)
                if dropdown_options:
                    inner_text = "Options: " + ", ".join([f"{opt['text']}{'*' if opt['selected'] else ''}" for opt in dropdown_options])
                    converted_node_name = "dropdown"

            if (
                (converted_node_name != "button" or meta == "")
                and converted_node_name != "link"
                and converted_node_name != "input"
                and converted_node_name != "img"
                and converted_node_name != "textarea"
            ) and inner_text.strip() == "" and placeholder == "":
                continue

            self.page_element_buffer[id_counter] = element

            if converted_node_name in ["input", "textarea"]:
                elements_of_interest.append(
                    f"""<{converted_node_name} id={id_counter}{meta} placeholder="{placeholder}">{inner_text}</{converted_node_name}>"""
                )
            elif inner_text != "": 
                elements_of_interest.append(
                    f"""<{converted_node_name} id={id_counter}{meta}>{inner_text}</{converted_node_name}>"""
                )
            else:
                elements_of_interest.append(
                    f"""<{converted_node_name} id={id_counter}{meta}/>"""
                )
            id_counter += 1

            # element_info = {
            #     "type": converted_node_name,
            #     "id": node_index,
            #     "meta": meta.strip(),
            #     "inner_text": inner_text.strip()
            # }
            
            # if placeholder:
            #     element_info["placeholder"] = placeholder
            
            # if converted_node_name == "dropdown":
            #     element_info["options"] = inner_text
            
            # elements_of_interest.append(str(element_info))

        # print("Parsing time: {:0.2f} seconds".format(time.time() - start))
        return elements_of_interest

    async def scroll(self, direction, steps=1, delay=1):
        for _ in range(steps):
            if direction.lower() == "up":
                await self.page.evaluate("(document.scrollingElement || document.body).scrollTop -= window.innerHeight;")
                print("Scrolled up")
            elif direction.lower() == "down":
                await self.page.evaluate("(document.scrollingElement || document.body).scrollTop += window.innerHeight;")
                print("Scrolled down")
            else:
                print("Invalid scroll direction. Use 'up' or 'down'.")
            await asyncio.sleep(delay)
        
        # Update the page_element_buffer after scrolling
        await self.crawl()

    async def old_click(self, node_index):
        # Find and click the element with the given node_index using JavaScript
        js_code = f"""
        (function(nodeIndex) {{
            function findElementByIndex(root, index) {{
                let count = 0;
                let result = null;
                
                function traverse(node) {{
                    if (count === index) {{
                        result = node;
                        return;
                    }}
                    count++;
                    for (let child of node.children) {{
                        traverse(child);
                        if (result) return;
                    }}
                }}
                
                traverse(root);
                return result;
            }}

            const element = findElementByIndex(document.body, {node_index});
            if (element) {{
                const nodeName = element.nodeName.toLowerCase();
                if (nodeName === 'select' || (nodeName === 'div' && element.getAttribute('role') === 'listbox')) {{
                    element.focus();
                }}
                element.click();
                if (nodeName === 'textarea' || nodeName === 'input') {{
                    element.focus();
                }}
                return {{
                    success: true,
                    nodeName: nodeName
                }};
            }}
            return {{ success: false }};
        }})({node_index})
        """
        
        result = await self.page.evaluate(js_code)
        
        if result and result.get('success'):
            print(f"Clicked element with node_index {node_index}")
            print(f"Element type: {result['nodeName']}")
        else:
            print(f"Could not find element with node_index {node_index}")

    async def click(self, id):
        await self.read()

        js = """
        links = document.getElementsByTagName("a");
        for (var i = 0; i < links.length; i++) {
            links[i].removeAttribute("target");
        }
        """
        await self.page.evaluate(js)

        element = self.page_element_buffer.get(int(id))
        if element:
            print(element)
            x = element.get("center_x")
            y = element.get("center_y")
            
            # Get the current scroll position
            scroll_x = await self.page.evaluate("window.pageXOffset")
            scroll_y = await self.page.evaluate("window.pageYOffset")
            
            # Calculate viewport-relative coordinates
            viewport_x = x - scroll_x
            viewport_y = y - scroll_y
            
            print(f"Clicking at viewport coordinates: {viewport_x}, {viewport_y}")
            
            node_name = element.get("node_name")
            
            if node_name == 'select' or (node_name == 'div' and element.get("node_meta") and 'role="listbox"' in element.get("node_meta")):
                # For dropdowns, we'll just focus and click to open it
                await self.page.evaluate(f"""
                    var element = document.elementFromPoint({viewport_x}, {viewport_y});
                    if (element) {{
                        element.focus();
                        element.click();
                    }}
                """)
            else:
                # Existing click logic for other elements
                await self.page.mouse.click(viewport_x, viewport_y)
            
            # If the element is a textarea or input, focus on it
            if element.get("node_name") in ["textarea", "input"]:
                await self.page.evaluate(f"""
                    var element = document.elementFromPoint({viewport_x}, {viewport_y});
                    if (element && element.tagName && typeof element.tagName.toLowerCase === 'function') {{
                        var tagName = element.tagName.toLowerCase();
                        if (tagName === 'textarea' || tagName === 'input') {{
                            element.focus();
                        }}
                    }}
                """)
        else:
            print("Could not find element")