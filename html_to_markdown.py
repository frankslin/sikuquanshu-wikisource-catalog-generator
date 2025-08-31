#!/usr/bin/env python3
"""
Convert HTML file to Markdown format.
Specifically designed for Chinese academic catalog format.
"""

import re
import sys
from html.parser import HTMLParser
from html import unescape

class HTMLToMarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.current_line = ""
        self.in_title = False
        self.in_h2 = False
        self.in_link = False
        self.in_font_small = False
        self.current_section = None  # Track current section (集, 史, 經, 子)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        elif tag == 'h2':
            self.in_h2 = True
        elif tag == 'a':
            self.in_link = True
        elif tag == 'br':
            self._flush_line()
        elif tag == 'font':
            for attr_name, attr_value in attrs:
                if attr_name == 'size' and attr_value == '-2':
                    self.in_font_small = True
        elif tag in ['ul', 'div']:
            self._flush_line()
            
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
            if self.current_line.strip():
                self.output.append(f"# {self.current_line.strip()}")
                self.current_line = ""
        elif tag == 'h2':
            self.in_h2 = False
            if self.current_line.strip():
                self.output.append(f"## {self.current_line.strip()}")
                self.current_line = ""
        elif tag == 'a':
            self.in_link = False
        elif tag == 'font':
            self.in_font_small = False
        elif tag in ['ul', 'div']:
            self._flush_line()
        elif tag == 'body':
            self._flush_line()
            
    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
            
        if self.in_title or self.in_h2:
            self.current_line += text
        elif self.in_link:
            # Add space before if line doesn't end with space and isn't empty
            if self.current_line and not self.current_line.endswith(' '):
                self.current_line += " "
            self.current_line += f"**{text}**"
        elif self.in_font_small:
            # Add space before if line doesn't end with space and isn't empty
            if self.current_line and not self.current_line.endswith(' '):
                self.current_line += " "
            self.current_line += f"*{text}*"
        else:
            if text != "&nbsp;":
                self.current_line += text + " "
    
    def _flush_line(self):
        if self.current_line.strip():
            self.output.append(self.current_line.strip())
            self.current_line = ""
    
    def get_markdown(self):
        self._flush_line()
        # Remove empty lines and clean up
        result = []
        for line in self.output:
            line = line.strip()
            if line:
                # Replace Japanese kanji "坿" with Chinese "附"
                line = line.replace('坿', '附')
                
                # Add bullet point for book entries (lines starting with **)
                if line.startswith('**') and not line.startswith('## '):
                    line = '- ' + line
                # Add volume numbers for volume entries
                elif '册' in line and ('第' in line or '首' in line):
                    # First detect section type in this line
                    if '部' in line:
                        for section_char in ['集', '史', '經', '子']:
                            if f'{section_char}部' in line:
                                self.current_section = section_char
                                break
                        else:
                            self.current_section = None
                    line = self._add_volume_numbers(line)
                # Detect section type for lines that only contain section info
                elif line.endswith('部'):
                    for section_char in ['集', '史', '經', '子']:
                        if f'{section_char}部' in line:
                            self.current_section = section_char
                            break
                    else:
                        self.current_section = None
                result.append(line)
        
        return '\n\n'.join(result)
    
    def _create_volume_links(self, volume_numbers, section_type=None):
        """Convert volume numbers to Wikimedia Commons links."""
        if section_type:
            # For main sections (集部, 史部, 經部, 子部)
            section_map = {
                '集': '%E9%9B%86%E9%83%A8',  # 集部
                '史': '%E5%8F%B2%E9%83%A8',  # 史部  
                '經': '%E7%B6%93%E9%83%A8',  # 經部
                '子': '%E5%AD%90%E9%83%A8'   # 子部
            }
            section_encoded = section_map.get(section_type, '%E8%A3%9C%E7%B7%A8')
            base_url = f"https://commons.wikimedia.org/wiki/File:%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8{section_encoded}{{:03d}}%E5%86%8A.pdf"
        else:
            # For supplement (補編)
            base_url = "https://commons.wikimedia.org/wiki/File:%E5%9B%9B%E5%BA%AB%E5%85%A8%E6%9B%B8%E5%AD%98%E7%9B%AE%E5%8F%A2%E6%9B%B8%E8%A3%9C%E7%B7%A8{:02d}%E5%86%8A.pdf"
        
        if isinstance(volume_numbers, str):
            # Handle comma-separated numbers like "21,22"
            if ',' in volume_numbers:
                nums = volume_numbers.split(',')
                links = [f"[{num.strip()}]({base_url.format(int(num.strip()))})" for num in nums]
                return ','.join(links)
            # Handle range like "21-22"  
            elif '-' in volume_numbers:
                nums = volume_numbers.split('-')
                links = [f"[{num.strip()}]({base_url.format(int(num.strip()))})" for num in nums]
                return '-'.join(links)
            # Single number
            else:
                return f"[{volume_numbers}]({base_url.format(int(volume_numbers))})"
        elif isinstance(volume_numbers, list):
            # Handle list of numbers
            return ','.join([f"[{num}]({base_url.format(int(num))})" for num in volume_numbers])
        else:
            return str(volume_numbers)

    def _add_volume_numbers(self, line):
        """Add volume numbers in parentheses for volume entries."""
        import re
        
        # Pattern for 第X第Y册 (consecutive volumes without separator)
        pattern5 = r'第([一二三四五六七八九十百千〇]+)第([一二三四五六七八九十百千〇]+)册'
        match5 = re.search(pattern5, line)
        if match5:
            chinese_num1 = match5.group(1)
            chinese_num2 = match5.group(2)
            arabic_num1 = self._chinese_to_arabic(chinese_num1)
            arabic_num2 = self._chinese_to_arabic(chinese_num2)
            volume_links = self._create_volume_links(f'{arabic_num1},{arabic_num2}', self.current_section)
            line = re.sub(pattern5, f'第{chinese_num1}、第{chinese_num2}册 ({volume_links})', line)
            return line
        
        # Pattern for 第X至Y册 (without second 第, check this first)
        # Use negative lookahead to ensure there's no 第 before the second number
        pattern4 = r'第([一二三四五六七八九十百千〇]+)至(?!第)([一二三四五六七八九十百千〇]+)册'
        match4 = re.search(pattern4, line)
        if match4:
            chinese_num1 = match4.group(1)
            chinese_num2 = match4.group(2)
            arabic_num1 = int(self._chinese_to_arabic(chinese_num1))
            arabic_num2 = int(self._chinese_to_arabic(chinese_num2))
            # Generate comma-separated list of all numbers
            numbers = [str(i) for i in range(arabic_num1, arabic_num2 + 1)]
            volume_links = self._create_volume_links(numbers, self.current_section)
            line = re.sub(pattern4, f'第{chinese_num1}至{chinese_num2}册 ({volume_links})', line)
            return line
        
        # Pattern for 第X至第第Y册 (with extra 第, check this first)
        pattern_extra = r'第([一二三四五六七八九十百千〇]+)至第第([一二三四五六七八九十百千〇]+)册'
        match_extra = re.search(pattern_extra, line)
        if match_extra:
            chinese_num1 = match_extra.group(1)
            chinese_num2 = match_extra.group(2)
            arabic_num1 = int(self._chinese_to_arabic(chinese_num1))
            arabic_num2 = int(self._chinese_to_arabic(chinese_num2))
            # Generate comma-separated list of all numbers
            numbers = [str(i) for i in range(arabic_num1, arabic_num2 + 1)]
            volume_links = self._create_volume_links(numbers, self.current_section)
            line = re.sub(pattern_extra, f'第{chinese_num1}至第{chinese_num2}册 ({volume_links})', line)
            return line
        
        # Pattern for 第X至第Y册 (check this second)
        pattern3 = r'第([一二三四五六七八九十百千〇]+)至第([一二三四五六七八九十百千〇]+)册'
        match3 = re.search(pattern3, line)
        if match3:
            chinese_num1 = match3.group(1)
            chinese_num2 = match3.group(2)
            arabic_num1 = int(self._chinese_to_arabic(chinese_num1))
            arabic_num2 = int(self._chinese_to_arabic(chinese_num2))
            # Generate comma-separated list of all numbers
            numbers = [str(i) for i in range(arabic_num1, arabic_num2 + 1)]
            volume_links = self._create_volume_links(numbers, self.current_section)
            line = re.sub(pattern3, f'第{chinese_num1}至第{chinese_num2}册 ({volume_links})', line)
            return line
        
        # Pattern for 第X・第Y册 (check this second to avoid double processing)
        # Include 〇 (zero) in the pattern
        pattern2 = r'第([一二三四五六七八九十百千〇]+)・第([一二三四五六七八九十百千〇]+)册'
        match2 = re.search(pattern2, line)
        if match2:
            chinese_num1 = match2.group(1)
            chinese_num2 = match2.group(2)
            arabic_num1 = self._chinese_to_arabic(chinese_num1)
            arabic_num2 = self._chinese_to_arabic(chinese_num2)
            volume_links = self._create_volume_links(f'{arabic_num1}-{arabic_num2}', self.current_section)
            line = re.sub(pattern2, f'第{chinese_num1}・第{chinese_num2}册 ({volume_links})', line)
            return line
        
        # Pattern for 第X册 (only if the compound patterns didn't match)
        # Include 〇 (zero) in the pattern
        pattern1 = r'第([一二三四五六七八九十百千〇]+)册'
        match1 = re.search(pattern1, line)
        if match1:
            chinese_num = match1.group(1)
            arabic_num = self._chinese_to_arabic(chinese_num)
            volume_link = self._create_volume_links(arabic_num, self.current_section)
            line = re.sub(pattern1, f'第{chinese_num}册 ({volume_link})', line)
        
        return line
    
    def _chinese_to_arabic(self, chinese_num):
        """Convert Chinese numerals to Arabic numerals."""
        chinese_dict = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '〇': 0, '零': 0, '百': 100, '千': 1000
        }
        
        if len(chinese_num) == 1:
            return str(chinese_dict.get(chinese_num, chinese_num))
        
        # Handle special cases first
        if chinese_num == '十':
            return '10'
        
        # For cases like "二〇" (20), "二一" (21), etc. - consecutive digits including zero
        if len(chinese_num) == 2 and all(c in '一二三四五六七八九〇零' for c in chinese_num):
            return str(chinese_dict[chinese_num[0]]) + str(chinese_dict[chinese_num[1]])
        
        # For cases like "一二三" (123), "二〇一" (201), etc. - consecutive digits
        if all(c in '一二三四五六七八九〇零' for c in chinese_num):
            return ''.join(str(chinese_dict[c]) for c in chinese_num)
        
        result = 0
        i = 0
        
        while i < len(chinese_num):
            char = chinese_num[i]
            if char not in chinese_dict:
                i += 1
                continue
                
            val = chinese_dict[char]
            
            if val == 10:  # 十
                if i == 0:  # 十 at the beginning (like 十一)
                    result += 10
                else:  # X十 (like 二十)
                    result = result * 10 if result > 0 else 10
            elif val == 100:  # 百
                result = result * 100 if result > 0 else 100
            elif val == 1000:  # 千
                result = result * 1000 if result > 0 else 1000
            else:  # 0-9
                if i + 1 < len(chinese_num):
                    next_char = chinese_num[i + 1]
                    if next_char == '十':
                        result += val * 10
                        i += 1  # Skip the 十
                    elif next_char in ['百', '千']:
                        result += val * chinese_dict[next_char]
                        i += 1  # Skip the 百/千
                    else:
                        result += val
                else:
                    result += val
            
            i += 1
        
        return str(result)

def convert_html_to_markdown(html_file_path, output_file_path):
    """Convert HTML file to Markdown format."""
    try:
        # Read HTML file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML and convert to Markdown
        converter = HTMLToMarkdownConverter()
        converter.feed(html_content)
        markdown_content = converter.get_markdown()
        
        # Write Markdown file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Successfully converted HTML to Markdown: {output_file_path}")
        
    except Exception as e:
        print(f"Error converting file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_markdown.py <input_html_file> [output_md_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # If output file not provided, create one based on input filename
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = input_file.rsplit('.', 1)[0] + '.md'
    
    convert_html_to_markdown(input_file, output_file)
