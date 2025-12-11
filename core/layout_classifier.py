import os
import json
from typing import Dict, List, Optional, Tuple
from loguru import logger
from .llm import call_llm

class LayoutClassifier:
    """
    Classifier that selects the most appropriate layout based on Intent, Context, and Data.
    """
    
    def __init__(self, layouts_dir: str = "layouts_json", extra_layout_dirs: Optional[List[str]] = None):
        self.layouts_dir = layouts_dir
        # Additional directories to search for custom layouts (e.g., "layout_json_custom")
        self.extra_layout_dirs = extra_layout_dirs or ["layout_json_custom"]
        self.demo_layouts = {}
        self.fixed_layouts = {}
        self.layouts_by_type = {}
        # Cached prompt resources
        self._middle_layouts_prompt_text: str = ""
        self._middle_prompt_template: Optional[str] = None
        self._load_demo_layouts()
        self._load_middle_prompt_template()
    
    def _load_demo_layouts(self):
        """Load layouts generically into a unified map by contents_type."""
        try:
            index_path = os.path.join(self.layouts_dir, "0_index.json")
            by_type: Dict[str, List[Dict]] = {}

            if not os.path.exists(index_path):
                logger.error(f"Index file not found: {index_path}")
            else:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

                for item in index_data:
                    if item.get("demo", False):
                        layout_file = item["file"].replace(".html", ".json")
                        layout_path = os.path.join(self.layouts_dir, layout_file)

                        if os.path.exists(layout_path):
                            try:
                                with open(layout_path, 'r', encoding='utf-8') as f_json:
                                    layout_data = json.load(f_json)
                                contents_type = (item.get("contents_type", "") or layout_data.get("contents_type", "") or "").strip() or "unknown"
                                by_type.setdefault(contents_type, []).append({
                                    "id": layout_file.replace(".json", ""),
                                    "name": item.get("name") or layout_data.get("name") or layout_file.replace(".json", ""),
                                    "description": layout_data.get("description", ""),
                                    "examples": layout_data.get("examples", []),
                                    "layout_data": layout_data
                                })
                            except Exception as e:
                                logger.warning(f"Failed to load layout file {layout_path}: {e}")
                        else:
                            logger.warning(f"Layout file not found: {layout_path}")

            # 2) Load from extra/custom directories
            for extra_dir in self.extra_layout_dirs:
                try:
                    if not os.path.exists(extra_dir):
                        logger.warning(f"Custom layouts directory not found: {extra_dir}")
                        continue
                    self._collect_layouts_from_directory(extra_dir, by_type)
                except Exception as e:
                    logger.error(f"Error while loading custom layouts from {extra_dir}: {e}")

            # Assign to instance: unified map
            self.layouts_by_type = by_type
            # Backward-compat mirrors
            self.demo_layouts["middle"] = by_type.get("middle", [])
            self.fixed_layouts = {k: v for k, v in by_type.items() if k != "middle"}

            # Cache prompt text for middle (for legacy prompt path)
            self._middle_layouts_prompt_text = self._build_middle_layouts_text(by_type.get("middle", []))

            logger.info("Layouts loaded (unified by contents_type)")
            logger.info(f"- Types: {list(by_type.keys())}")
            logger.info(f"- Counts: { {k: len(v or []) for k, v in by_type.items()} }")

        except Exception as e:
            logger.error(f"Error while loading layouts: {e}")

    def _extract_parameters_for_prompt(self, layout_data: Dict) -> Dict:
        """Extract parameters section for prompt display with fallbacks."""
        try:
            if isinstance(layout_data, dict):
                params = layout_data.get("parameters")
                if isinstance(params, dict):
                    return params
                props = layout_data.get("properties")
                if isinstance(props, dict):
                    params = props.get("parameters")
                    if isinstance(params, dict):
                        return params
        except Exception:
            pass
        return {}

    def _build_middle_layouts_text(self, middle_layouts: List[Dict]) -> str:
        """Prebuild the layouts listing text for prompts and cache it."""
        import json as _json
        lines: List[str] = []
        for i, layout in enumerate(middle_layouts):
            try:
                name = layout.get('name', '')
                desc = layout.get('description', '')
                examples = layout.get('examples', [])
                params_obj = self._extract_parameters_for_prompt(layout.get('layout_data', {}))
                params = _json.dumps(params_obj, ensure_ascii=False, indent=2)
                lines.append(f"\n[{i}] {name}:")
                lines.append(f"Description: {desc}")
                lines.append(f"Examples: {examples}")
                lines.append(f"Parameters: {params}")
            except Exception as e:
                logger.warning(f"Failed to build prompt text for layout index {i}: {e}")
        return "\n".join(lines)

    def _load_middle_prompt_template(self) -> None:
        """Load and cache the middle layout classification prompt template."""
        if self._middle_prompt_template:
            return
        template_path_candidates = [
            os.path.join("core", "prompt", "layout_classifier_middle_en.txt"),
            os.path.join(os.path.dirname(__file__), "prompt", "layout_classifier_middle.txt"),
        ]
        for template_path in template_path_candidates:
            if os.path.exists(template_path):
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        self._middle_prompt_template = f.read()
                    return
                except Exception as e:
                    logger.error(f"Failed to read prompt template: {template_path} - {e}")
        # Fallback inline template
        logger.warning("Prompt template not found. Using inline prompt.")
        self._middle_prompt_template = (
            "You are an expert UI layout classifier. Choose the most appropriate middle layout.\n\n"
            "User Info:\nIntent: {{INTENT}}\nContext:\n{{CONTEXT}}\nUser Data:\n{{USER_DATA}}\n\n"
            "Available Middle Layouts:\n{{LAYOUTS}}\n\n"
            "Response format:\nSELECTED_INDEX: <number>\n"
        )

    def refresh_layouts(self) -> Dict:
        """Reload layouts from disk and rebuild caches. Returns summary."""
        self._load_demo_layouts()
        self._load_middle_prompt_template()
        return self.get_demo_layouts_summary()

    def _collect_layouts_from_directory(self, target_dir: str, by_type: Dict[str, List[Dict]]) -> None:
        """Scan a directory for JSON layout files and merge them into the provided by_type map.
        Custom layouts do not rely on 0_index.json. Every *.json will be considered."""
        if not os.path.isdir(target_dir):
            logger.warning(f"Target layout directory is not a directory: {target_dir}")
            return

        for filename in os.listdir(target_dir):
            if not filename.lower().endswith('.json'):
                continue
            if filename == '0_index.json':
                # Skip any index files in custom directories
                continue

            file_path = os.path.join(target_dir, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read custom layout file {file_path}: {e}")
                continue

            contents_type = (layout_data.get("contents_type", "") or "").strip() or "unknown"
            layout_id = filename.replace('.json', '')
            layout_name = layout_data.get("name", layout_id)
            layout_description = layout_data.get("description", "")
            layout_examples = layout_data.get("examples", [])

            by_type.setdefault(contents_type, []).append({
                "id": layout_id,
                "name": layout_name,
                "description": layout_description,
                "examples": layout_examples,
                "layout_data": layout_data
            })
    
    async def classify_layouts(self, intent: str, context: Dict, user_data: str, slots: List[str], model_name: str = "gpt-4o") -> List[Dict]:
        """
        Select layouts for a list of requested layout types.
        
        Args:
            intent: user intent
            context: user context
            user_data: text summary for LLM
            slots: list of layout types, e.g., ["middle", "bottom"]
            model_name: LLM model name
        Returns:
            List of selected layout dicts aligned to the order of slots
        """
        if not isinstance(slots, list) or not slots:
            return []

        # Build mapping from layout type to needed count and positions
        type_to_positions: Dict[str, List[int]] = {}
        for idx, layout_type in enumerate(slots):
            if isinstance(layout_type, str) and layout_type:
                type_to_positions.setdefault(layout_type, []).append(idx)

        # For each type, pick required_count layouts
        selected_by_type: Dict[str, List[Dict]] = {}
        for layout_type, positions in type_to_positions.items():
            required_count = max(1, len(positions))

            # Candidate pool by type (generic lookup without special-casing)
            candidates = self.layouts_by_type.get(layout_type, [])

            if not candidates:
                logger.warning(f"No candidates available for layout_type='{layout_type}'")
                selected_by_type[layout_type] = []
                continue

            # If only one candidate exists, return it without LLM
            if len(candidates) == 1:
                selected_by_type[layout_type] = [candidates[0]] * required_count
                continue

            selected_list = await self._select_layouts_generic(
                intent=intent,
                context=context,
                user_data=user_data,
                candidates=candidates,
                layout_type=layout_type,
                count=required_count,
                model_name=model_name,
            )

            # Ensure enough items by deterministic fill
            if len(selected_list) < required_count:
                picked = list(selected_list)
                for i in range(required_count - len(selected_list)):
                    picked.append(candidates[i % len(candidates)])
                selected_list = picked

            selected_by_type[layout_type] = selected_list[:required_count]

        # Recompose into ordered list
        results: List[Dict] = [None] * len(slots)
        for layout_type, positions in type_to_positions.items():
            items = selected_by_type.get(layout_type, [])
            for i, pos in enumerate(positions):
                if i < len(items):
                    results[pos] = items[i]
                else:
                    results[pos] = None

        return results
    
    async def _select_middle_layout(self, intent: str, context: Dict, user_data: str, model_name: str) -> Optional[Dict]:
        """Select the most suitable middle-type layout"""
        if not self.demo_layouts.get("middle"):
            logger.warning("No available middle layouts")
            return None
        
        middle_layouts = self.demo_layouts["middle"]
        
        # Use LLM to classify layouts (load from prompt template file)
        prompt = self._create_middle_classification_prompt(intent, context, user_data, middle_layouts)
        
        # Retry up to 3 iterations on parsing failure or exceptions
        last_error: Optional[Exception] = None
        for attempt in range(1, 4):
            try:
                response = await call_llm(prompt, model_name=model_name)
                selected_index = self._parse_classification_response(response)
                
                if selected_index is not None and 0 <= selected_index < len(middle_layouts):
                    selected_layout = middle_layouts[selected_index]
                    logger.info(f"Selected middle layout: {selected_layout['id']} ({selected_layout['name']}) on attempt {attempt}")
                    return selected_layout
                else:
                    logger.warning(f"Invalid layout index: {selected_index}; attempt {attempt} of 3")
            except Exception as e:
                last_error = e
                logger.error(f"Error during middle layout classification (attempt {attempt}/3): {e}")
        
        # Fallback: return the first middle layout
        if last_error:
            logger.error(f"Falling back to first middle layout due to errors. Last error: {last_error}")
        else:
            logger.warning("Falling back to first middle layout due to repeated invalid indices")
        return middle_layouts[0]
    
    def _create_middle_classification_prompt(self, intent: str, context: Dict, user_data: str, middle_layouts: List[Dict]) -> str:
        """Create a prompt for classifying middle layouts using cached template and layouts text."""
        # Ensure caches are ready
        if not self._middle_layouts_prompt_text:
            self._middle_layouts_prompt_text = self._build_middle_layouts_text(self.demo_layouts.get("middle", []))
        if not self._middle_prompt_template:
            self._load_middle_prompt_template()

        prompt = self._middle_prompt_template
        prompt = prompt.replace("{{INTENT}}", str(intent))
        prompt = prompt.replace("{{CONTEXT}}", json.dumps(context, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{{USER_DATA}}", str(user_data))
        prompt = prompt.replace("{{LAYOUTS}}", self._middle_layouts_prompt_text)
        return prompt
    
    def _parse_classification_response(self, response: str) -> Optional[int]:
        """Extract layout index from classification response"""
        try:
            # Extract X from "SELECTED_INDEX: X"
            if "SELECTED_INDEX:" in response:
                parts = response.split("SELECTED_INDEX:")
                if len(parts) > 1:
                    index_str = parts[1].strip().split()[0]
                    return int(index_str)
            
            # If the response contains only numbers
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                return int(numbers[0])
                
        except Exception as e:
            logger.error(f"Error parsing classification response: {e}")
        
        return None

    def _build_candidates_text(self, candidates: List[Dict]) -> str:
        import json as _json
        lines: List[str] = []
        for i, layout in enumerate(candidates):
            try:
                name = layout.get('name', '')
                desc = layout.get('description', '')
                examples = layout.get('examples', [])
                params_obj = self._extract_parameters_for_prompt(layout.get('layout_data', {}))
                params = _json.dumps(params_obj, ensure_ascii=False, indent=2)
                lines.append(f"\n[{i}] {name}:")
                lines.append(f"Description: {desc}")
                lines.append(f"Examples: {examples}")
                lines.append(f"Parameters: {params}")
            except Exception as e:
                logger.warning(f"Failed to build text for candidate index {i}: {e}")
        return "\n".join(lines)

    def _create_generic_prompt(self, intent: str, context: Dict, user_data: str, candidates_text: str, layout_type: str, count: int) -> str:
        return (
            "You are an expert UI layout classifier.\n"
            f"Choose the most appropriate {layout_type} layout(s) for the user's need.\n\n"
            f"Required count: {count}. Provide EXACTLY {count} unique indices.\n\n"
            "User Info:\n"
            f"Intent: {intent}\n"
            f"Context:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n"
            f"User Data:\n{user_data}\n\n"
            f"Available {layout_type.capitalize()} Layouts:\n{candidates_text}\n\n"
            "Response format (strict JSON): {\n  \"indices\": [i1, i2, ...]\n}\n"
        )

    def _parse_multi_indices(self, response: str, max_index: int, max_count: int) -> List[int]:
        try:
            import json as _json
            # Try JSON first
            data = _json.loads(response)
            if isinstance(data, dict) and isinstance(data.get("indices"), list):
                nums = [int(x) for x in data["indices"]]
            else:
                raise ValueError("No indices array")
        except Exception:
            # Fallback regex numbers
            import re
            nums = [int(n) for n in re.findall(r"\d+", response)]

        # Sanitize, unique, in-range
        seen = set()
        cleaned: List[int] = []
        for n in nums:
            if 0 <= n < max_index and n not in seen:
                seen.add(n)
                cleaned.append(n)
            if len(cleaned) >= max_count:
                break
        return cleaned

    async def _select_layouts_generic(self, intent: str, context: Dict, user_data: str, candidates: List[Dict], layout_type: str, count: int, model_name: str) -> List[Dict]:
        """LLM-assisted selection for any layout type with multi-select support."""
        if not candidates:
            return []
        if count <= 0:
            return []

        # Single selection path uses the same generic pipeline for simplicity

        text = self._build_candidates_text(candidates)
        prompt = self._create_generic_prompt(intent, context, user_data, text, layout_type, count)

        last_error: Optional[Exception] = None
        for attempt in range(1, 4):
            try:
                response = await call_llm(prompt, model_name=model_name)
                idxs = self._parse_multi_indices(response, max_index=len(candidates), max_count=count)
                if idxs:
                    picked = [candidates[i] for i in idxs[:count]]
                    # Ensure size
                    if len(picked) < count:
                        # Fill deterministically without duplicates
                        used = set(id(x) for x in picked)
                        for cand in candidates:
                            if id(cand) not in used:
                                picked.append(cand)
                                used.add(id(cand))
                                if len(picked) >= count:
                                    break
                    return picked
                else:
                    logger.warning(f"No valid indices parsed for {layout_type}; attempt {attempt}/3")
            except Exception as e:
                last_error = e
                logger.error(f"Error during {layout_type} layout classification (attempt {attempt}/3): {e}")

        # Fallback: first N
        if last_error:
            logger.error(f"Falling back to first {count} {layout_type} layouts. Last error: {last_error}")
        return candidates[:count]
    
    def get_demo_layouts_summary(self) -> Dict:
        """Return summary information of demo layouts"""
        return {
            "middle_layouts_count": len(self.demo_layouts.get("middle", [])),
            "fixed_layouts": list(self.fixed_layouts.keys()),
            "middle_layouts": [
                {"id": layout["id"], "name": layout["name"], "examples": layout["examples"]} 
                for layout in self.demo_layouts.get("middle", [])
            ]
        }
    
    def get_layout_by_id(self, layout_id: str) -> Optional[Dict]:
        """Return specific layout information by ID"""
        # Search in middle layouts
        for layout in self.demo_layouts.get("middle", []):
            if layout["id"] == layout_id:
                return layout
        
        # Search in fixed layouts
        for layout_type, layout_list in self.fixed_layouts.items():
            for layout_data in layout_list:
                if layout_data["id"] == layout_id:
                    return layout_data
        
        return None
