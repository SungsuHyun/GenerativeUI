from .llm import call_llm, read_prompt
import os
from typing import Optional
from loguru import logger
import html

def _clean_llm_output(raw_code: str) -> str:
    """
    Cleans the raw code string received from the LLM.
    - Removes markdown code block fences (e.g., ```html and ```).
    - Replaces escaped quotes with regular quotes.
    - Decodes HTML entities.
    """
    import html
    
    cleaned_code = raw_code.strip()
    
    # Remove ```html prefix
    if cleaned_code.startswith("```html"):
        cleaned_code = cleaned_code[7:]
    
    # Remove ``` suffix
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-3]
        
    # Un-escape quotes
    cleaned_code = cleaned_code.replace('\\"', '"')
    
    # Decode HTML entities (특히 &quot; -> ")
    cleaned_code = html.unescape(cleaned_code)

    return cleaned_code.strip()

def _ensure_font_consistency(html_code: str) -> str:
    """
    Ensures Samsung One UI font is consistently applied throughout the HTML.
    - Replaces any non-Samsung fonts with One UI font
    - Adds global font style with web font loading
    - Ensures !important is used for font declarations
    - Fixes HTML entity encoding issues in font names
    """
    import re
    
    # Samsung One UI font specification
    samsung_font = '"One UI Sans App VF", "Samsung One UI", "Segoe UI", Roboto, sans-serif'
    
    # Fix HTML entities in font names first
    html_code = html_code.replace('&quot;One UI Sans App VF&quot;', '"One UI Sans App VF"')
    html_code = html_code.replace("&quot;", '"')
    
    # Replace common fonts with Samsung One UI font
    font_patterns = [
        (r'font-family:\s*["\']?Source Code Pro["\']?[^;]*', f'font-family: {samsung_font}'),
        (r'font-family:\s*["\']?Arial["\']?[^;]*', f'font-family: {samsung_font}'),
        (r'font-family:\s*["\']?Helvetica["\']?[^;]*', f'font-family: {samsung_font}'),
        (r'font-family:\s*["\']?system-ui["\']?[^;]*', f'font-family: {samsung_font}'),
        (r'font-family:\s*["\']?-apple-system["\']?[^;]*', f'font-family: {samsung_font}'),
        (r'font-family:\s*["\']?sans-serif["\']?(?![^"\']*One UI)', f'font-family: {samsung_font}'),
        # One UI Sans App VF 단독 사용 시 fallback 추가
        (r'font-family:\s*["\']One UI Sans App VF["\']\s*(?:,\s*sans-serif)?(?![^;]*Roboto)', f'font-family: {samsung_font}'),
    ]
    
    cleaned_html = html_code
    for pattern, replacement in font_patterns:
        cleaned_html = re.sub(pattern, replacement, cleaned_html, flags=re.IGNORECASE)
    
    # Enhanced global font style with web font loading and better fallbacks
    global_font_style = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body, div, span, p, h1, h2, h3, h4, h5, h6, a, li, ul, ol, input, button, label, textarea {
  font-family: "One UI Sans App VF", "Samsung One UI", "Inter", "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
}

/* Fallback for One UI Sans App VF */
@font-face {
  font-family: 'One UI Sans App VF';
  src: local('One UI Sans App VF'), local('Samsung One UI'), local('Inter');
  font-display: swap;
}
</style>'''
    
    # Check if style block already exists
    if '<style>' not in cleaned_html.lower():
        # Add style block at the end
        cleaned_html += '\n' + global_font_style
    else:
        # Update existing style block to include enhanced font consistency
        style_pattern = r'(<style[^>]*>)(.*?)(</style>)'
        def update_style_block(match):
            style_start = match.group(1)
            style_content = match.group(2)
            style_end = match.group(3)
            
            # Check if font import already exists
            if '@import' not in style_content and 'Inter' not in style_content:
                font_import = "\n@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');\n"
                style_content = font_import + style_content
            
            # Check if enhanced font-family rule already exists
            if 'font-family:' not in style_content or 'Inter' not in style_content:
                font_rule = '\nbody, div, span, p, h1, h2, h3, h4, h5, h6, a, li, ul, ol, input, button, label, textarea {\n  font-family: "One UI Sans App VF", "Samsung One UI", "Inter", "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;\n}\n\n@font-face {\n  font-family: \'One UI Sans App VF\';\n  src: local(\'One UI Sans App VF\'), local(\'Samsung One UI\'), local(\'Inter\');\n  font-display: swap;\n}'
                style_content += font_rule
            
            return style_start + style_content + style_end
        
        cleaned_html = re.sub(style_pattern, update_style_block, cleaned_html, flags=re.DOTALL | re.IGNORECASE)
    
    logger.info("Enhanced font consistency check and correction applied")
    return cleaned_html

def _load_layout_samples(intent: str) -> str:
    """
    레이아웃 샘플 폴더에서 HTML과 TXT 파일을 로드합니다.
    현재는 샘플 5번만 사용하도록 하드코딩되어 있습니다.
    """
    layout_samples_dir = "core/layout_samples"
    
    # 현재는 5번 샘플만 사용
    sample_id = 5
    html_path = os.path.join(layout_samples_dir, f"{sample_id}.html")
    txt_path = os.path.join(layout_samples_dir, f"{sample_id}.txt")
    
    if not (os.path.exists(html_path) and os.path.exists(txt_path)):
        logger.warning(f"Layout sample {sample_id} not found")
        return ""
    
    try:
        # HTML 파일 읽기
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read().strip()
        
        # TXT 파일 읽기
        with open(txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read().strip()
        
        # HTML과 TXT 내용을 함께 포맷팅
        formatted_sample = f"Sample 1)\n"
        formatted_sample += f"HTML Layout:\n~~~\n{html_content}\n~~~\n\n"
        formatted_sample += f"Analysis & Usage:\n{txt_content}\n"
        
        logger.info(f"Loaded layout sample: {os.path.basename(html_path)} + {os.path.basename(txt_path)}")
        return formatted_sample
        
    except Exception as e:
        logger.error(f"Error loading {html_path} or {txt_path}: {e}")
        return ""


async def generate_ui_code_step(intent: str, context: dict, user_data: str, ui_requirements: str, model_name: Optional[str] = 'gpt-4.1-mini') -> str:
    """
    Step 4: Generates the actual UI code based on the final component connection structure (JSON).
    """
    logger.info("Reading prompt for UI generator.")
    prompt_template = read_prompt("core/prompt/ui_generator_layout.txt")
    
    # 레이아웃 샘플 로드
    layout_templates = _load_layout_samples(intent)
    
    prompt = prompt_template.replace("||Intent||", intent)
    prompt = prompt.replace("||Context||", "\n".join(context))
    prompt = prompt.replace("||User_Data||", user_data)
    prompt = prompt.replace("||CARD_LAYOUT_TEMPLATES||", layout_templates)
    # prompt = prompt.replace("||UI_Requirement||", ui_requirements)
    
    logger.info(f"Calling LLM for UI code generation with model: {model_name}")
    raw_code = await call_llm(prompt, model_name=model_name)
    logger.info("LLM call for UI code generation finished.")
    
    cleaned_code = _clean_llm_output(raw_code)
    final_code = _ensure_font_consistency(cleaned_code)
    
    return final_code 