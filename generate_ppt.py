#!/usr/bin/env python3
"""Generate impressive graphical PowerPoint presentation for Ultron Project."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, PP_PARAGRAPH_ALIGNMENT
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import nsmap

# Color Palette
COLORS = {
    'dark_blue': RGBColor(0, 51, 102),
    'medium_blue': RGBColor(70, 130, 180),
    'light_blue': RGBColor(100, 149, 237),
    'sky_blue': RGBColor(135, 206, 250),
    'gold': RGBColor(255, 215, 0),
    'white': RGBColor(255, 255, 255),
    'black': RGBColor(0, 0, 0),
    'dark_gray': RGBColor(50, 50, 50),
    'green': RGBColor(34, 139, 34),
    'red': RGBColor(178, 34, 34),
    'purple': RGBColor(128, 0, 128),
    'orange': RGBColor(255, 140, 0),
    'teal': RGBColor(0, 128, 128),
    'navy': RGBColor(0, 0, 128),
    'slate': RGBColor(112, 128, 144),
}


def set_gradient_fill(shape, start_color, end_color):
    """Add gradient fill to a shape."""
    fill = shape.fill
    fill.gradient()
    fill.gradient_angle = 90
    # Start color
    fill.gradient_stops[0].color.rgb = start_color
    # End color
    fill.gradient_stops[1].color.rgb = end_color


def add_decorative_corner(slide, position, color):
    """Add decorative corner element."""
    x, y = position
    size = Inches(0.8)
    
    # Main corner triangle-like shape
    corner = slide.shapes.add_shape(
        MSO_SHAPE.ISOSCELES_TRIANGLE, x, y, size, size
    )
    corner.fill.solid()
    corner.fill.fore_color.rgb = color
    corner.line.fill.background()
    
    # Accent circle
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, x + Inches(0.1), y + Inches(0.1), Inches(0.2), Inches(0.2)
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['white']
    circle.line.fill.background()


def add_icon_circle(slide, x, y, size, color, icon_type):
    """Add an icon in a circle."""
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, x, y, size, size
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    
    # Add simple icon representation based on type
    if icon_type == 'mic':
        # Microphone icon
        mic_top = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, x + size * 0.35, y + size * 0.15, size * 0.3, size * 0.35
        )
        mic_top.fill.solid()
        mic_top.fill.fore_color.rgb = COLORS['white']
        mic_top.line.fill.background()
        
        mic_mid = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, x + size * 0.4, y + size * 0.55, size * 0.2, size * 0.25
        )
        mic_mid.fill.solid()
        mic_mid.fill.fore_color.rgb = COLORS['white']
        mic_mid.line.fill.background()
        
    elif icon_type == 'brain':
        # Brain icon (circles)
        for i in range(3):
            brain_circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                x + size * (0.2 + i * 0.25),
                y + size * 0.35,
                size * 0.25,
                size * 0.25
            )
            brain_circle.fill.solid()
            brain_circle.fill.fore_color.rgb = COLORS['white']
            brain_circle.line.fill.background()
    
    elif icon_type == 'gear':
        # Gear/cog icon
        gear = slide.shapes.add_shape(
            MSO_SHAPE.HEXAGON, x + size * 0.15, y + size * 0.15, size * 0.7, size * 0.7
        )
        gear.fill.solid()
        gear.fill.fore_color.rgb = COLORS['white']
        gear.line.fill.background()


def add_process_arrow(slide, x, y, width, height, color):
    """Add a process arrow shape."""
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW, x, y, width, height
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.fill.background()


def add_infographic_box(slide, x, y, width, height, color, title, value):
    """Add an infographic-style box with title and value."""
    # Background box
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, x, y, width, height
    )
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.1), width - Inches(0.2), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # Value
    value_box = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.6), width - Inches(0.2), height - Inches(0.7))
    value_frame = value_box.text_frame
    value_frame.word_wrap = True
    p = value_frame.paragraphs[0]
    p.text = value
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER


def add_progress_bar(slide, x, y, width, height, progress, color):
    """Add a progress bar."""
    # Background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, x, y, width, height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['slate']
    bg.line.fill.background()
    
    # Progress
    progress_width = width * progress
    prog = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, x, y, progress_width, height
    )
    prog.fill.solid()
    prog.fill.fore_color.rgb = color
    prog.line.fill.background()


def add_connection_line(slide, x1, y1, x2, y2, color, line_width=Pt(2)):
    """Add a connecting line between two points using a thin rectangle."""
    # Calculate dimensions
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    # Use the smaller dimension as thickness
    if width > height:
        # Horizontal line
        if height == 0:
            height = line_width
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, min(x1, x2), min(y1, y2) - line_width/2, width, line_width
        )
    else:
        # Vertical line
        if width == 0:
            width = line_width
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, min(x1, x2) - line_width/2, min(y1, y2), line_width, height
        )
    
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()


def add_diagram_box(slide, x, y, width, height, color, text, is_center=False):
    """Add a diagram box for flowcharts."""
    shape_type = MSO_SHAPE.OVAL if is_center else MSO_SHAPE.ROUNDED_RECTANGLE
    box = slide.shapes.add_shape(shape_type, x, y, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.color.rgb = COLORS['dark_blue']
    box.line.width = Pt(2)
    
    text_box = slide.shapes.add_textbox(x + Inches(0.1), y + height/2 - Inches(0.25), width - Inches(0.2), Inches(0.5))
    text_frame = text_box.text_frame
    text_frame.word_wrap = True
    p = text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER


def add_title_slide(prs):
    """Add an impressive title slide with modern design."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Gradient background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    set_gradient_fill(bg, COLORS['dark_blue'], COLORS['navy'])
    bg.line.fill.background()
    
    # Decorative geometric shapes
    # Top left accent
    accent1 = slide.shapes.add_shape(
        MSO_SHAPE.PENTAGON, Inches(-0.5), Inches(-0.5), Inches(3), Inches(3)
    )
    accent1.fill.solid()
    accent1.fill.fore_color.rgb = COLORS['light_blue']
    accent1.fill.fore_color.brightness = 0.3
    accent1.line.fill.background()
    
    # Bottom right accent
    accent2 = slide.shapes.add_shape(
        MSO_SHAPE.HEXAGON, prs.slide_width - Inches(2.5), prs.slide_height - Inches(2.5), Inches(3), Inches(3)
    )
    accent2.fill.solid()
    accent2.fill.fore_color.rgb = COLORS['gold']
    accent2.fill.fore_color.brightness = 0.3
    accent2.line.fill.background()
    
    # Decorative circles
    for i, (cx, cy, size, color) in enumerate([
        (Inches(1), Inches(1), Inches(0.5), COLORS['light_blue']),
        (prs.slide_width - Inches(1.5), Inches(2), Inches(0.4), COLORS['sky_blue']),
        (Inches(2), prs.slide_height - Inches(2), Inches(0.6), COLORS['gold']),
    ]):
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx, cy, size, size)
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.fill.fore_color.brightness = 0.4
        circle.line.fill.background()
    
    # Icon circles
    add_icon_circle(slide, Inches(0.5), Inches(3.5), Inches(1.2), COLORS['light_blue'], 'mic')
    add_icon_circle(slide, prs.slide_width - Inches(1.7), Inches(4.5), Inches(1.2), COLORS['gold'], 'brain')
    
    # Main title box with gradient background
    title_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2), Inches(7), Inches(2.5)
    )
    set_gradient_fill(title_bg, COLORS['medium_blue'], COLORS['dark_blue'])
    title_bg.line.color.rgb = COLORS['white']
    title_bg.line.width = Pt(3)
    
    # Main title
    title_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(7), Inches(2))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = "ULTRON"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(80)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.space_after = Pt(12)
    
    p = title_frame.add_paragraph()
    p.text = "Desktop Voice Assistant"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['sky_blue']
    p.space_after = Pt(8)
    
    p = title_frame.add_paragraph()
    p.text = "with Local AI Brain"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(28)
    p.font.color.rgb = COLORS['gold']
    
    # Subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(2), Inches(5), Inches(6), Inches(1.5))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.word_wrap = True
    
    p = subtitle_frame.paragraphs[0]
    p.text = "Specialization Project"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.space_after = Pt(12)
    
    p = subtitle_frame.add_paragraph()
    p.text = "Lakshya Mittal | 24215121"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(18)
    p.font.color.rgb = COLORS['sky_blue']
    
    # Bottom banner
    bottom_banner = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(6.5), Inches(6), Inches(0.4)
    )
    bottom_banner.fill.solid()
    bottom_banner.fill.fore_color.rgb = COLORS['gold']
    bottom_banner.line.fill.background()


def add_section_divider(prs, chapter_num, chapter_title, color):
    """Add a visually striking section divider."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Full background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    set_gradient_fill(bg, color, COLORS['dark_blue'])
    bg.line.fill.background()
    
    # Diagonal accent
    diagonal = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE, Inches(8), 0, Inches(2.5), Inches(7.5)
    )
    diagonal.fill.solid()
    diagonal.fill.fore_color.rgb = COLORS['white']
    diagonal.fill.fore_color.brightness = 0.2
    diagonal.line.fill.background()
    
    # Large chapter number
    num_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
    num_frame = num_box.text_frame
    num_frame.word_wrap = True
    
    p = num_frame.paragraphs[0]
    p.text = f"CHAPTER {chapter_num}"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(72)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.space_after = Pt(24)
    
    # Chapter title
    title_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(8), Inches(2))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = chapter_title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = COLORS['gold']
    
    # Decorative elements
    circle1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.5), Inches(-0.5), Inches(2), Inches(2))
    circle1.fill.solid()
    circle1.fill.fore_color.rgb = COLORS['white']
    circle1.fill.fore_color.brightness = 0.3
    circle1.line.fill.background()
    
    circle2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, prs.slide_width - Inches(1.5), prs.slide_height - Inches(1.5), Inches(2), Inches(2))
    circle2.fill.solid()
    circle2.fill.fore_color.rgb = COLORS['white']
    circle2.fill.fore_color.brightness = 0.3
    circle2.line.fill.background()


def add_content_slide(prs, title, content_items, color=COLORS['dark_blue']):
    """Add a content slide with modern design."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Side accent bar
    side_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.3), prs.slide_height
    )
    set_gradient_fill(side_bar, color, COLORS['dark_blue'])
    side_bar.line.fill.background()
    
    # Title bar
    title_bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.2), Inches(9), Inches(1)
    )
    title_bar.fill.solid()
    title_bar.fill.fore_color.rgb = color
    title_bar.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Content boxes
    y_pos = Inches(1.5)
    for i, item in enumerate(content_items):
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), y_pos, Inches(8.6), Inches(0.7)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = COLORS['white'] if i % 2 == 0 else RGBColor(240, 248, 255)
        box.line.color.rgb = color
        box.line.width = Pt(2)
        
        text_box = slide.shapes.add_textbox(Inches(1), y_pos + Inches(0.1), Inches(8), Inches(0.5))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        p = text_frame.paragraphs[0]
        p.text = f"• {item}"
        p.font.size = Pt(18)
        p.font.color.rgb = COLORS['dark_gray']
        
        y_pos += Inches(0.8)
    
    # Decorative corner
    add_decorative_corner(slide, (prs.slide_width - Inches(0.8), prs.slide_height - Inches(0.8)), color)


def add_two_column_slide(prs, title, left_items, right_items, color=COLORS['dark_blue']):
    """Add a two-column slide with visual separation."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Top bar
    top_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.4)
    )
    set_gradient_fill(top_bar, color, COLORS['dark_blue'])
    top_bar.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.1), Inches(9), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Left column background
    left_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.8), Inches(4.3), Inches(6)
    )
    left_bg.fill.solid()
    left_bg.fill.fore_color.rgb = RGBColor(240, 248, 255)
    left_bg.line.color.rgb = color
    left_bg.line.width = Pt(3)
    
    # Right column background
    right_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(0.8), Inches(4.3), Inches(6)
    )
    right_bg.fill.solid()
    right_bg.fill.fore_color.rgb = RGBColor(230, 240, 250)
    right_bg.line.color.rgb = color
    right_bg.line.width = Pt(3)
    
    # Left content
    y_pos = Inches(1.2)
    for item in left_items:
        text_box = slide.shapes.add_textbox(Inches(0.8), y_pos, Inches(3.7), Inches(0.6))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        p = text_frame.paragraphs[0]
        p.text = f"• {item}"
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark_gray']
        
        y_pos += Inches(0.7)
    
    # Right content
    y_pos = Inches(1.2)
    for item in right_items:
        text_box = slide.shapes.add_textbox(Inches(5.5), y_pos, Inches(3.7), Inches(0.6))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        p = text_frame.paragraphs[0]
        p.text = f"• {item}"
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark_gray']
        
        y_pos += Inches(0.7)


def add_infographic_slide(prs, title, metrics):
    """Add an infographic-style slide with visual metrics."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(245, 247, 250)
    bg.line.fill.background()
    
    # Title bar
    title_bar = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.2), Inches(9), Inches(0.8)
    )
    set_gradient_fill(title_bar, COLORS['dark_blue'], COLORS['medium_blue'])
    title_bar.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Metric boxes in a grid
    colors = [COLORS['light_blue'], COLORS['medium_blue'], COLORS['gold'], COLORS['teal']]
    positions = [
        (Inches(0.7), Inches(1.5)),
        (Inches(4.9), Inches(1.5)),
        (Inches(0.7), Inches(3.5)),
        (Inches(4.9), Inches(3.5)),
    ]
    
    for i, (metric, value) in enumerate(metrics[:4]):
        x, y = positions[i]
        add_infographic_box(slide, x, y, Inches(4), Inches(1.5), colors[i], metric, value)
    
    # Additional metrics as progress bars
    y_pos = Inches(5.5)
    for i, (metric, value) in enumerate(metrics[4:6]):
        text_box = slide.shapes.add_textbox(Inches(0.7), y_pos, Inches(8.6), Inches(0.4))
        text_frame = text_box.text_frame
        p = text_frame.paragraphs[0]
        p.text = metric
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLORS['dark_gray']
        
        # Parse percentage from value
        if '%' in value:
            progress = float(value.replace('%', '')) / 100
        else:
            progress = 0.8
        
        add_progress_bar(slide, Inches(0.7), y_pos + Inches(0.4), Inches(8.6), Inches(0.2), progress, colors[i])
        
        y_pos += Inches(0.8)


def add_flowchart_slide(prs, title, steps):
    """Add a flowchart slide showing process flow."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['dark_blue']
    
    # Draw flowchart
    box_width = Inches(1.8)
    box_height = Inches(0.8)
    start_x = Inches(0.8)
    y_pos = Inches(1.5)
    
    colors = [COLORS['light_blue'], COLORS['medium_blue'], COLORS['gold'], COLORS['teal'], COLORS['green']]
    
    for i, step in enumerate(steps):
        x = start_x + (i % 3) * (box_width + Inches(0.5))
        y = y_pos + (i // 3) * (box_height + Inches(0.8))
        
        # Box
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, x, y, box_width, box_height
        )
        box.fill.solid()
        box.fill.fore_color.rgb = colors[i % len(colors)]
        box.line.color.rgb = COLORS['dark_blue']
        box.line.width = Pt(2)
        
        # Text
        text_box = slide.shapes.add_textbox(x + Inches(0.1), y + Inches(0.2), box_width - Inches(0.2), box_height - Inches(0.4))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = step
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER
        
        # Arrow to next
        if i < len(steps) - 1 and (i + 1) % 3 != 0:
            arrow_x = x + box_width + Inches(0.1)
            add_process_arrow(slide, arrow_x, y + Inches(0.3), Inches(0.3), Inches(0.2), COLORS['dark_gray'])
        
        # Downward arrow for new row
        if i == 2 and len(steps) > 3:
            add_process_arrow(slide, start_x + box_width, y + box_height + Inches(0.1), Inches(0.2), Inches(0.3), COLORS['dark_gray'])


def add_features_grid_slide(prs, title, features):
    """Add a slide with features in a grid layout."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(240, 248, 255)
    bg.line.fill.background()
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['dark_blue']
    
    # Feature cards
    card_width = Inches(2.8)
    card_height = Inches(1.8)
    positions = [
        (Inches(0.6), Inches(1.5)),
        (Inches(3.6), Inches(1.5)),
        (Inches(6.6), Inches(1.5)),
        (Inches(0.6), Inches(3.8)),
        (Inches(3.6), Inches(3.8)),
        (Inches(6.6), Inches(3.8)),
    ]
    
    colors = [COLORS['light_blue'], COLORS['medium_blue'], COLORS['sky_blue'], COLORS['gold'], COLORS['teal'], COLORS['purple']]
    
    for i, (feature, icon) in enumerate(features[:6]):
        x, y = positions[i]
        
        # Card background
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_width, card_height
        )
        card.fill.solid()
        card.fill.fore_color.rgb = COLORS['white']
        card.line.color.rgb = colors[i]
        card.line.width = Pt(3)
        
        # Icon circle
        icon_circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, x + Inches(0.1), y + Inches(0.1), Inches(0.5), Inches(0.5)
        )
        icon_circle.fill.solid()
        icon_circle.fill.fore_color.rgb = colors[i]
        icon_circle.line.fill.background()
        
        # Feature text
        text_box = slide.shapes.add_textbox(x + Inches(0.7), y + Inches(0.7), card_width - Inches(0.9), Inches(1))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = feature
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLORS['dark_gray']


def add_architecture_slide(prs, title, components):
    """Add a system architecture diagram slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['dark_blue']
    
    # Central brain/core
    center_x = Inches(4.5)
    center_y = Inches(3)
    
    # Core circle
    core = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, center_x - Inches(1.2), center_y - Inches(1.2), Inches(2.4), Inches(2.4)
    )
    set_gradient_fill(core, COLORS['gold'], COLORS['medium_blue'])
    core.line.color.rgb = COLORS['dark_blue']
    core.line.width = Pt(4)
    
    # Core text
    core_text = slide.shapes.add_textbox(center_x - Inches(1), center_y - Inches(0.4), Inches(2), Inches(0.8))
    core_frame = core_text.text_frame
    p = core_frame.paragraphs[0]
    p.text = "BRAIN"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Surrounding modules
    module_positions = [
        (Inches(1.5), Inches(3), "EARS", COLORS['light_blue']),
        (Inches(7.5), Inches(3), "VOICE", COLORS['teal']),
        (Inches(4.5), Inches(1), "UI", COLORS['purple']),
        (Inches(4.5), Inches(5), "ACTIONS", COLORS['green']),
    ]
    
    for x, y, name, color in module_positions:
        # Module box
        module = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, x - Inches(0.8), y - Inches(0.4), Inches(1.6), Inches(0.8)
        )
        module.fill.solid()
        module.fill.fore_color.rgb = color
        module.line.color.rgb = COLORS['dark_blue']
        module.line.width = Pt(2)
        
        # Module text
        module_text = slide.shapes.add_textbox(x - Inches(0.7), y - Inches(0.3), Inches(1.4), Inches(0.6))
        module_frame = module_text.text_frame
        p = module_frame.paragraphs[0]
        p.text = name
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        
        # Connection line to center
        add_connection_line(slide, x + Inches(0.8) if x < center_x else x - Inches(0.8),
                           y, center_x, center_y, COLORS['dark_gray'], Pt(3))


def add_comparison_slide(prs, title, left_title, right_title, left_items, right_items):
    """Add a comparison slide with visual distinction."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    
    p = title_frame.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['dark_blue']
    
    # Left side header
    left_header = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.2), Inches(4.3), Inches(0.6)
    )
    left_header.fill.solid()
    left_header.fill.fore_color.rgb = COLORS['green']
    left_header.line.fill.background()
    
    left_header_text = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(4.3), Inches(0.4))
    left_header_frame = left_header_text.text_frame
    p = left_header_frame.paragraphs[0]
    p.text = left_title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Right side header
    right_header = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), Inches(1.2), Inches(4.3), Inches(0.6)
    )
    right_header.fill.solid()
    right_header.fill.fore_color.rgb = COLORS['red']
    right_header.line.fill.background()
    
    right_header_text = slide.shapes.add_textbox(Inches(5.2), Inches(1.3), Inches(4.3), Inches(0.4))
    right_header_frame = right_header_text.text_frame
    p = right_header_frame.paragraphs[0]
    p.text = right_title
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # Left content
    y_pos = Inches(2)
    for item in left_items:
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), y_pos, Inches(4.3), Inches(0.6)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(235, 250, 235)
        box.line.color.rgb = COLORS['green']
        box.line.width = Pt(2)
        
        text_box = slide.shapes.add_textbox(Inches(0.7), y_pos + Inches(0.1), Inches(3.9), Inches(0.4))
        text_frame = text_box.text_frame
        p = text_frame.paragraphs[0]
        p.text = f"✓ {item}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLORS['dark_gray']
        
        y_pos += Inches(0.7)
    
    # Right content
    y_pos = Inches(2)
    for item in right_items:
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.2), y_pos, Inches(4.3), Inches(0.6)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(250, 235, 235)
        box.line.color.rgb = COLORS['red']
        box.line.width = Pt(2)
        
        text_box = slide.shapes.add_textbox(Inches(5.4), y_pos + Inches(0.1), Inches(3.9), Inches(0.4))
        text_frame = text_box.text_frame
        p = text_frame.paragraphs[0]
        p.text = f"✗ {item}"
        p.font.size = Pt(14)
        p.font.color.rgb = COLORS['dark_gray']
        
        y_pos += Inches(0.7)


def add_thank_you_slide(prs):
    """Add an impressive thank you slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Gradient background
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    set_gradient_fill(bg, COLORS['dark_blue'], COLORS['navy'])
    bg.line.fill.background()
    
    # Decorative circles
    for i, (cx, cy, size, color) in enumerate([
        (Inches(-0.5), Inches(-0.5), Inches(3), COLORS['light_blue']),
        (prs.slide_width - Inches(2.5), Inches(-0.5), Inches(3), COLORS['gold']),
        (Inches(-0.5), prs.slide_height - Inches(2.5), Inches(3), COLORS['teal']),
        (prs.slide_width - Inches(2.5), prs.slide_height - Inches(2.5), Inches(3), COLORS['sky_blue']),
    ]):
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx, cy, size, size)
        circle.fill.solid()
        circle.fill.fore_color.rgb = color
        circle.fill.fore_color.brightness = 0.3
        circle.line.fill.background()
    
    # Main thank you
    thank_you_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
    thank_you_frame = thank_you_box.text_frame
    thank_you_frame.word_wrap = True
    
    p = thank_you_frame.paragraphs[0]
    p.text = "THANK YOU"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(80)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.space_after = Pt(24)
    
    p = thank_you_frame.add_paragraph()
    p.text = "Questions?"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(48)
    p.font.color.rgb = COLORS['gold']
    
    # Contact information
    contact_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(4.5), Inches(6), Inches(2)
    )
    contact_box.fill.solid()
    contact_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    contact_box.fill.fore_color.brightness = 0.1
    contact_box.line.color.rgb = COLORS['gold']
    contact_box.line.width = Pt(3)
    
    contact_text = slide.shapes.add_textbox(Inches(2), Inches(4.7), Inches(6), Inches(1.8))
    contact_frame = contact_text.text_frame
    contact_frame.word_wrap = True
    
    p = contact_frame.paragraphs[0]
    p.text = "Lakshya Mittal"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.space_after = Pt(8)
    
    p = contact_frame.add_paragraph()
    p.text = "24215121"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(20)
    p.font.color.rgb = COLORS['sky_blue']
    p.space_after = Pt(8)
    
    p = contact_frame.add_paragraph()
    p.text = "School of Sciences, CHRIST (Deemed to be University)"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS['white']


def main():
    """Generate the complete impressive PowerPoint presentation."""
    prs = Presentation()
    
    # Slide 1: Title
    add_title_slide(prs)
    
    # Chapter 1 Divider
    add_section_divider(prs, 1, "Introduction", COLORS['dark_blue'])
    
    # Slide 2: Introduction
    add_content_slide(prs, "Introduction", [
        "Voice assistants revolutionize human-computer interaction",
        "Commercial assistants (Siri, Alexa, Google) rely on cloud processing",
        "Privacy concerns with cloud-based voice data transmission",
        "Local AI enables privacy-preserving, offline-capable assistants",
        "Ultron demonstrates fully local voice assistant on macOS"
    ])
    
    # Slide 3: Motivation
    add_content_slide(prs, "Motivation", [
        "Explore feasibility of local voice assistant",
        "Understand voice assistant technology at fundamental level",
        "Apply academic concepts in AI and software engineering",
        "Demonstrate privacy-preserving computing",
        "Provide practical alternative to cloud-based assistants"
    ])
    
    # Slide 4: Problem Statement
    add_content_slide(prs, "Problem Statement", [
        "Develop fully functional voice assistant on local hardware",
        "Implement accurate wake-word detection",
        "Achieve reliable speech recognition in diverse environments",
        "Design effective intent parsing for natural language",
        "Integrate with system APIs for task execution",
        "Deploy local LLM for conversational AI",
        "Balance response quality with performance"
    ])
    
    # Slide 5: Objectives
    add_content_slide(prs, "Objectives", [
        "Implement wake-word detection ('Hey Ultron')",
        "Achieve reliable speech recognition",
        "Develop intent parsing system",
        "Integrate system APIs (web search, app launch, file ops)",
        "Implement text-to-speech synthesis",
        "Integrate local LLM (Ollama) for AI conversation",
        "Create intuitive user interface with visual feedback"
    ])
    
    # Chapter 2 Divider
    add_section_divider(prs, 2, "Existing Work", COLORS['medium_blue'])
    
    # Slide 6: Commercial Assistants
    add_content_slide(prs, "Commercial Voice Assistants", [
        "Siri, Alexa, Google Assistant, Cortana",
        "Sophisticated capabilities with multi-turn conversations",
        "Extensive service integrations and ecosystems",
        "Require internet connectivity",
        "Privacy concerns with cloud processing",
        "Limited user control over AI models"
    ], COLORS['medium_blue'])
    
    # Slide 7: Open Source Alternatives
    add_content_slide(prs, "Open Source Alternatives", [
        "Mycroft, Jasper, research prototypes",
        "Emphasize privacy and local processing",
        "Customizable but limited capabilities",
        "Require technical expertise",
        "Lack extensive service integrations"
    ], COLORS['medium_blue'])
    
    # Slide 8: Theoretical Background
    add_two_column_slide(prs, "Theoretical Background", [
        "Signal Processing: Audio capture, noise reduction, feature extraction",
        "Machine Learning: Deep neural networks for speech recognition",
        "NLP: Intent classification, entity extraction, dialogue management",
        "HCI: User interface design and feedback mechanisms"
    ], [
        "Speech Recognition: Statistical to deep learning approaches",
        "NLU: Rule-based to LLM-based understanding",
        "TTS: Concatenative to neural synthesis",
        "Wake-word detection: Specialized low-latency models"
    ], COLORS['medium_blue'])
    
    # Chapter 3 Divider
    add_section_divider(prs, 3, "Implementation", COLORS['light_blue'])
    
    # Slide 9: System Architecture
    add_architecture_slide(prs, "System Architecture", [])
    
    # Slide 10: Tools & Technologies
    add_features_grid_slide(prs, "Tools & Technologies", [
        ("Python 3.9+", "code"),
        ("PyAudio", "mic"),
        ("SpeechRecognition", "mic"),
        ("Tkinter", "gear"),
        ("Ollama", "brain"),
        ("macOS Tools", "gear"),
    ])
    
    # Slide 11: Module Implementation - Ears
    add_content_slide(prs, "Ears Module Implementation", [
        "Microphone initialization and calibration",
        "Continuous background listening",
        "Wake-word detection using speech recognition",
        "Command transcription with timeout handling",
        "Audio processing for noise reduction",
        "Callbacks for wake detection and command capture"
    ], COLORS['light_blue'])
    
    # Slide 12: Module Implementation - Brain
    add_content_slide(prs, "Brain Module Implementation", [
        "Hybrid intent parsing: rule-based + AI fallback",
        "Pattern matching for known commands",
        "Parameter extraction from natural language",
        "Ollama integration for unknown queries",
        "Conversation context management",
        "Special state handling (confirmation, quiz, file writing)"
    ], COLORS['light_blue'])
    
    # Slide 13: Module Implementation - Actions
    add_content_slide(prs, "Actions Module Implementation", [
        "Web searching (Google, YouTube)",
        "Application launching (VS Code, Calculator, etc.)",
        "File operations (create folders, write files)",
        "System control (volume, lock, shutdown, restart)",
        "Memory operations (remember/recall information)",
        "Timers and reminders",
        "Quiz mode and translation"
    ], COLORS['light_blue'])
    
    # Slide 14: Module Implementation - Voice & UI
    add_two_column_slide(prs, "Voice & UI Modules", [
        "Voice Module:",
        "macOS native 'say' command",
        "Configurable speech rate",
        "Voice selection options",
        "Cross-platform TTS support (pyttsx3)"
    ], [
        "UI Module:",
        "Blue HUD-style interface",
        "Status indicators (awake, listening, processing)",
        "Conversation history display",
        "Manual text input option",
        "Microphone button for manual activation"
    ], COLORS['light_blue'])
    
    # Slide 15: Testing & Validation
    add_flowchart_slide(prs, "Testing & Validation Process", [
        "Manual Testing",
        "Automated Tests",
        "Ollama Check",
        "Wake Detection",
        "Speech Accuracy",
        "AI Integration",
        "End-to-End"
    ])
    
    # Chapter 4 Divider
    add_section_divider(prs, 4, "Results", COLORS['sky_blue'])
    
    # Slide 16: Performance Results
    add_infographic_slide(prs, "Performance Evaluation", [
        ("Wake Detection", "1-2 sec"),
        ("Speech Accuracy", "90-95%"),
        ("Intent Accuracy", "95%"),
        ("Command Success", "98%"),
        ("AI Response (Simple)", "2-5 sec"),
        ("AI Response (Complex)", "10-20 sec"),
    ])
    
    # Slide 17: Comparative Analysis
    add_comparison_slide(prs, "Comparative Analysis", "Ultron", "Commercial Assistants", [
        "All processing local",
        "Offline capability",
        "User model control",
        "No cloud dependency",
        "Privacy focused"
    ], [
        "Cloud processing",
        "Internet required",
        "Fixed AI models",
        "Extensive integrations",
        "Better performance"
    ])
    
    # Slide 18: Challenges & Solutions
    add_content_slide(prs, "Challenges & Solutions", [
        "Speech recognition in noisy environments → Calibration and error handling",
        "Wake-word detection latency → Optimized recognition intervals",
        "AI response time variability → Smaller models, status updates",
        "macOS version compatibility → Standard system commands and APIs",
        "Thread management for concurrency → Careful synchronization",
        "Module coupling → Refactoring, clear interfaces"
    ], COLORS['sky_blue'])
    
    # Chapter 5 Divider
    add_section_divider(prs, 5, "Conclusion", COLORS['dark_blue'])
    
    # Slide 19: Conclusion
    add_content_slide(prs, "Conclusion & Future Scope", [
        "Successfully demonstrated local voice assistant feasibility",
        "Achieved privacy-preserving AI with offline capability",
        "Modular architecture enables easy extension",
        "Valuable learning experience in AI, speech processing, and software engineering",
        "Future: Offline speech recognition (Whisper)",
        "Future: Improved wake-word detection",
        "Future: Cross-platform support (Windows/Linux)",
        "Future: Performance optimization with GPU acceleration"
    ])
    
    # Slide 20: Thank You
    add_thank_you_slide(prs)
    
    # Save the presentation
    output_path = "/Users/lakshyamittal/Downloads/Ultron_Impressive_Presentation.pptx"
    prs.save(output_path)
    print(f"Impressive presentation saved successfully to {output_path}")
    print(f"Total slides: {len(prs.slides)}")


if __name__ == "__main__":
    main()
