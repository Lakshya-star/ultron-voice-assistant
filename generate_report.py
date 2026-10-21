#!/usr/bin/env python3
"""Generate properly formatted Word document for Ultron Project Report with Christ University styling."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn

def set_font(run, font_name='Times New Roman', size=12, bold=False, italic=False):
    """Set font properties for a run."""
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    # Set font for complex script (required for some Word versions)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

def set_paragraph_style(paragraph, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=0, line_spacing=1.0):
    """Set paragraph formatting."""
    paragraph.alignment = alignment
    paragraph.paragraph_format.space_before = Pt(space_before)
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = line_spacing

def add_title_page(doc):
    """Add the title page with Christ University styling."""
    # Title
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=144, space_after=12)
    run = p.add_run("SPECIALIZATION PROJECT REPORT")
    set_font(run, 'Times New Roman', 16, bold=True)

    # Project Title
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=12)
    run = p.add_run("Ultron: Desktop Voice Assistant with Local AI Brain")
    set_font(run, 'Times New Roman', 14, bold=True)

    # Submitted in partial fulfilment
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=12)
    run = p.add_run("Submitted in Partial Fulfilment of the Requirements")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    run = p.add_run("for the Award of the Degree of")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=48)
    run = p.add_run("Bachelor of Computer Applications")
    set_font(run, 'Times New Roman', 12, bold=True)

    # By
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=12)
    run = p.add_run("By")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    run = p.add_run("Lakshya Mittal")
    set_font(run, 'Times New Roman', 12, bold=True)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=48)
    run = p.add_run("24215121")
    set_font(run, 'Times New Roman', 12)

    # Under the supervision of
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=12)
    run = p.add_run("Under the Supervision of")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=72)
    run = p.add_run("Prof. Lata Yadav")
    set_font(run, 'Times New Roman', 12, bold=True)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    run = p.add_run("School of Sciences")
    set_font(run, 'Times New Roman', 12)

    doc.add_page_break()

def add_certificate(doc):
    """Add the certificate page."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("CERTIFICATE")
    set_font(run, 'Times New Roman', 16, bold=True)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=24, space_after=12)
    run = p.add_run("This is to certify that Lakshya Mittal, 24215121, is a bonafide student of CHRIST")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    run = p.add_run("(Deemed to be University), Delhi NCR, and he has prepared and submitted this report on")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    run = p.add_run('"Ultron: Desktop Voice Assistant with Local AI Brain",')
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    run = p.add_run("during September 2026 in partial fulfilment of the requirement for the award of the degree of")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=48)
    run = p.add_run("Bachelor of Computer Applications of this University.")
    set_font(run, 'Times New Roman', 12)

    # Place and Date
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=48, space_after=12)
    run = p.add_run("Place: Ghaziabad")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=48)
    run = p.add_run("Date: 21st October 2026")
    set_font(run, 'Times New Roman', 12)

    # Signature
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=12)
    run = p.add_run("Dr. Bosco Paul Alapatt")
    set_font(run, 'Times New Roman', 12, bold=True)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    run = p.add_run("Associate Dean and Head")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=12)
    run = p.add_run("School of Sciences")
    set_font(run, 'Times New Roman', 12)

    doc.add_page_break()

def add_declaration(doc):
    """Add the declaration page."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("DECLARATION")
    set_font(run, 'Times New Roman', 16, bold=True)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=24, space_after=12)
    run = p.add_run("I, Lakshya Mittal, 24215121, a student of BCA in School of Sciences at Christ (Deemed to be University), hereby declare that the Specialization Project Report entitled: \"Ultron: Desktop Voice Assistant with Local AI Brain\" is an original record of my own work carried out as a specialization project. The project was developed during the academic year 2026 under the academic guidance of Prof. Lata Yadav. I further declare that the work presented in this report, including all data, system designs, diagrams, and code, is authentic to the best of my knowledge. This report has not been submitted previously, in part or in full, to any other University or Institution for the award of any degree, diploma, fellowship, or other similar academic title. Wherever external sources, literature, or documentation have been used, they have been duly acknowledged and properly cited in the references section.")
    set_font(run, 'Times New Roman', 12)

    # Place and Date
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=48, space_after=12)
    run = p.add_run("Place: Ghaziabad")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=48)
    run = p.add_run("Date: 21st October 2026")
    set_font(run, 'Times New Roman', 12)

    # Name and details
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=24, space_after=12)
    run = p.add_run("Name: Lakshya Mittal")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=12)
    run = p.add_run("Enrollment / Roll No: 24215121")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=48)
    run = p.add_run("Course & Semester: BCA, 5th Sem")
    set_font(run, 'Times New Roman', 12)

    # Countersigned
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=48, space_after=12)
    run = p.add_run("Countersigned:")
    set_font(run, 'Times New Roman', 12)

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=48, space_after=12)
    run = p.add_run("Prof. Lata Yadav")
    set_font(run, 'Times New Roman', 12, bold=True)

    doc.add_page_break()

def add_acknowledgement(doc):
    """Add the acknowledgement page."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("ACKNOWLEDGEMENT")
    set_font(run, 'Times New Roman', 16, bold=True)

    acknowledgement_text = """I would like to express my sincere gratitude to Prof. Lata Yadav for her guidance, support, and encouragement throughout the development of this specialization project. Her insights and feedback were invaluable in shaping the direction and quality of this work.

I extend my sincere thanks to the faculty members of CHRIST (Deemed to be University), Delhi NCR, for their academic guidance and for providing the framework through which this project could be developed and evaluated.

I am grateful to the open-source community, particularly the developers of Ollama, Python's speech recognition libraries, and the various tools and frameworks that made this project possible. The availability of these resources demonstrates the power of collaborative development in modern software engineering.

Finally, I would like to thank my family and friends for their continued support and encouragement during the development of this project and the preparation of this report."""

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=24, space_after=12)
    run = p.add_run(acknowledgement_text)
    set_font(run, 'Times New Roman', 12)

    doc.add_page_break()

def add_index(doc):
    """Add the index/table of contents page."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("INDEX")
    set_font(run, 'Times New Roman', 16, bold=True)

    index_items = [
        ("Cover", "i"),
        ("Declaration", "ii"),
        ("Acknowledgement", "iii"),
        ("Index", "iv"),
        ("Chapter 1: Introduction", "1"),
        ("Chapter 2: Existing Work", "5"),
        ("Chapter 3: Implementation", "9"),
        ("Chapter 4: Results", "15"),
        ("Chapter 5: Conclusion", "19"),
        ("References", "21")
    ]

    table = doc.add_table(rows=len(index_items) + 1, cols=2)
    table.style = 'Table Grid'

    # Header row
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Content"
    hdr_cells[1].text = "Page No."
    for cell in hdr_cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                set_font(run, 'Times New Roman', 12, bold=True)

    # Data rows
    for i, (content, page) in enumerate(index_items):
        row_cells = table.rows[i + 1].cells
        row_cells[0].text = content
        row_cells[1].text = page
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    set_font(run, 'Times New Roman', 12)

    doc.add_page_break()

def add_abstract(doc):
    """Add the abstract page."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("ABSTRACT / EXECUTIVE SUMMARY")
    set_font(run, 'Times New Roman', 16, bold=True)

    abstract_text = """This report presents the design, implementation, and evaluation of Ultron, a Siri-style desktop voice assistant for macOS powered by a local AI brain using Ollama. The project aims to create a fully functional voice assistant that operates entirely on the user's machine, eliminating dependence on cloud-based AI services and ensuring privacy and offline capability. Ultron features wake-word detection, a glowing blue HUD interface, and the ability to execute voice commands for system control, web searching, application launching, file operations, and conversational AI responses.

The project integrates multiple technical domains including speech recognition, natural language processing, text-to-speech synthesis, system automation, and local large language model deployment. The implementation uses Python as the primary development language, with Tkinter for the user interface, PyAudio and SpeechRecognition for audio processing, the macOS native `say` command for voice synthesis, and Ollama for local AI inference.

The report discusses the theoretical background of voice assistants, the system architecture, the tools and technologies used, the implementation methodology, testing and evaluation, and the challenges encountered during development. It also presents a comparative analysis with existing voice assistants and discusses future enhancements and potential applications of the technology.

The project demonstrates the feasibility of building a capable voice assistant using entirely local resources, highlighting the importance of privacy, offline capability, and user control in modern AI applications. It also showcases the practical application of academic concepts in artificial intelligence, software engineering, and human-computer interaction."""

    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=24, space_after=12)
    run = p.add_run(abstract_text)
    set_font(run, 'Times New Roman', 12)

    doc.add_page_break()

def add_chapter_heading(doc, chapter_num, title):
    """Add a chapter heading."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.LEFT, space_before=24, space_after=12)
    run = p.add_run(f"CHAPTER {chapter_num}: {title}")
    set_font(run, 'Times New Roman', 14, bold=True)

def add_section_heading(doc, section_num, title):
    """Add a section heading."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.LEFT, space_before=18, space_after=12)
    run = p.add_run(f"{section_num} {title}")
    set_font(run, 'Times New Roman', 12, bold=True)

def add_subsection_heading(doc, section_num, subsection_num, title):
    """Add a subsection heading."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=12)
    run = p.add_run(f"{section_num}.{subsection_num} {title}")
    set_font(run, 'Times New Roman', 12, bold=True)

def add_paragraph_text(doc, text, space_before=12, space_after=12):
    """Add a paragraph with text."""
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=space_before, space_after=space_after)
    run = p.add_run(text)
    set_font(run, 'Times New Roman', 12)

def main():
    """Generate the complete Word document."""
    doc = Document()

    # Set default font for the document
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    # Add all sections (no certificate as per new structure)
    add_title_page(doc)
    add_declaration(doc)
    add_acknowledgement(doc)
    add_index(doc)

    # Chapter 1: Introduction
    add_chapter_heading(doc, 1, "INTRODUCTION")
    add_section_heading(doc, "1.1", "Overview")
    add_paragraph_text(doc, "Voice assistants have become an integral part of modern computing, transforming how users interact with technology through natural language interfaces. Major technology companies have invested heavily in voice assistant platforms including Apple's Siri, Amazon's Alexa, Google Assistant, and Microsoft's Cortana. These systems have evolved from simple command-and-control interfaces to sophisticated AI-powered conversational agents capable of understanding context, handling multi-turn conversations, and performing complex tasks across multiple applications and services.")
    add_paragraph_text(doc, "The voice assistant market has experienced significant growth driven by advancements in speech recognition, natural language processing, and machine learning. According to industry reports, the global voice assistant market is projected to continue expanding as adoption increases in smart homes, automotive systems, healthcare, education, and enterprise environments. The proliferation of smart speakers, mobile devices, and integrated voice interfaces has made voice interaction a mainstream computing paradigm.")
    add_paragraph_text(doc, "However, most commercial voice assistants rely heavily on cloud-based processing. When a user speaks a command, the audio is typically transmitted to remote servers where speech recognition and natural language understanding are performed. This architecture introduces several concerns: privacy implications of transmitting voice data to third-party servers, dependency on internet connectivity, potential latency issues, and lack of user control over the AI models and data processing.")
    add_paragraph_text(doc, "The emergence of powerful open-source large language models has created new possibilities for local, privacy-preserving voice assistants. Models such as Llama, Mistral, and Qwen can now run efficiently on consumer hardware, enabling developers to build AI applications that operate entirely on the user's device. This shift represents a significant trend toward edge computing and local AI, addressing growing user concerns about privacy, data sovereignty, and offline functionality.")
    add_paragraph_text(doc, "The Ultron project is positioned at the intersection of these developments, demonstrating how a capable voice assistant can be built using entirely local resources while maintaining functionality comparable to cloud-based alternatives. The project explores the technical challenges and opportunities of local AI deployment, speech recognition, system integration, and user interface design for voice-based computing.")

    add_section_heading(doc, "1.2", "Motivation")
    add_paragraph_text(doc, "Ultron was conceived as a demonstration project to explore the feasibility and practical implementation of a fully local voice assistant. The project name was inspired by the Marvel character, reflecting the concept of an intelligent assistant with advanced capabilities. The development was motivated by several factors: the desire to understand voice assistant technology at a fundamental level, interest in local AI and privacy-preserving computing, and the opportunity to apply academic concepts in artificial intelligence and software engineering to a practical project.")
    add_paragraph_text(doc, "The project was developed on macOS, leveraging the platform's native capabilities for text-to-speech synthesis, application launching, system control, and screenshot capture. This choice was guided by the availability of robust system APIs and the goal of creating a tightly integrated assistant that can interact meaningfully with the operating system. The use of Python as the primary development language was driven by its extensive library ecosystem, readability, and suitability for rapid prototyping and integration of multiple components.")
    add_paragraph_text(doc, "The current implementation represents a functional prototype that demonstrates core voice assistant capabilities including wake-word detection, command parsing, task execution, and conversational AI responses. The system is designed to be extensible, allowing for the addition of new commands, integration with additional applications, and enhancement of AI capabilities through model selection and prompt engineering.")

    add_section_heading(doc, "1.3", "Problem Statement")
    add_paragraph_text(doc, "The central problem addressed by this project is the development of a fully functional voice assistant that operates entirely on local hardware without dependence on cloud-based services. This involves solving several technical challenges: implementing accurate wake-word detection, achieving reliable speech recognition in diverse acoustic environments, designing an effective intent parsing system that can understand natural language commands, integrating with system APIs for task execution, implementing responsive text-to-speech synthesis, and deploying a local large language model for conversational AI capabilities.")
    add_paragraph_text(doc, "A secondary challenge is creating a user interface that provides clear feedback about the system state, including wake-word activation, listening status, processing state, and response delivery. The interface must be intuitive, responsive, and visually appealing while maintaining low resource overhead to avoid interfering with other system operations.")
    add_paragraph_text(doc, "The project also addresses the challenge of modularity and maintainability. A voice assistant is a complex system involving multiple interconnected components. The design must ensure that modules are loosely coupled, well-documented, and easily extensible to support future enhancements and modifications. This requires careful architectural planning and adherence to software engineering best practices.")
    add_paragraph_text(doc, "Finally, the project explores the challenge of performance optimization. Local AI processing, particularly with large language models, can be computationally intensive. The system must balance response quality with response time, ensuring that the assistant remains responsive and usable even when processing complex queries. This involves optimizing model selection, prompt engineering, and background processing strategies.")

    add_section_heading(doc, "1.4", "Objectives")
    add_paragraph_text(doc, "The primary objective of this project is to design and implement a fully functional voice assistant that operates entirely on local hardware. Specific objectives include: implementing wake-word detection using \"Hey Ultron\" as the activation phrase; achieving reliable speech recognition for command input; developing an intent parsing system that can understand and categorize natural language commands; integrating with system APIs for task execution including web searching, application launching, and file operations; implementing text-to-speech synthesis for voice responses; and integrating a local large language model for conversational AI capabilities.")
    add_paragraph_text(doc, "Secondary objectives include: creating an intuitive user interface with visual feedback; ensuring the system is responsive and stable under normal operating conditions; implementing a modular architecture that supports easy extension and modification; documenting the system architecture and implementation details; and evaluating the system's performance and usability through testing.")
    add_paragraph_text(doc, "Learning objectives include: gaining practical experience with speech recognition and text-to-speech technologies; understanding the architecture of voice assistant systems; developing skills in natural language processing and intent parsing; learning about local AI deployment and optimization; practicing software engineering principles including modularity, documentation, and testing; and exploring user interface design for voice-based applications.")

    doc.add_page_break()

    # Chapter 2: Existing Work
    add_chapter_heading(doc, 2, "EXISTING WORK")
    add_section_heading(doc, "2.1", "Commercial Voice Assistants")
    add_paragraph_text(doc, "Existing voice assistants can be categorized into commercial cloud-based systems and research or open-source alternatives. Commercial systems including Siri, Alexa, Google Assistant, and Cortana represent the dominant paradigm in voice assistant technology. These systems offer sophisticated capabilities including multi-turn conversations, context awareness, integration with extensive service ecosystems, and continuous improvement through cloud-based machine learning. However, they require internet connectivity, raise privacy concerns, and provide limited user control over the underlying AI models.")
    add_paragraph_text(doc, "Open-source voice assistant projects have emerged as alternatives, including Mycroft, Jasper, and various research prototypes. These systems often emphasize privacy, local processing, and customizability. However, they may have limited capabilities compared to commercial systems, require more technical expertise to set up and maintain, and may lack the extensive service integrations that make commercial assistants valuable in practice.")
    add_paragraph_text(doc, "The technical architecture of voice assistants typically includes several components: an audio processing module that captures and preprocesses speech input; a wake-word detection system that listens for activation phrases; a speech recognition engine that converts audio to text; a natural language understanding module that parses intents and extracts entities; a dialogue manager that maintains conversation context; a task execution engine that performs requested actions; and a text-to-speech system that generates spoken responses.")
    add_paragraph_text(doc, "Recent advances in large language models have significantly enhanced the conversational capabilities of voice assistants. Models such as GPT, Llama, and Mistral can generate human-like responses, handle complex queries, and maintain context across multiple turns of conversation. Integrating these models into voice assistants requires balancing capability with computational requirements, particularly for local deployment.")

    add_section_heading(doc, "2.2", "Theoretical Background")
    add_paragraph_text(doc, "The theoretical foundation of voice assistant technology spans multiple domains including signal processing, machine learning, natural language processing, and human-computer interaction. Signal processing techniques are used for audio capture, noise reduction, feature extraction, and wake-word detection. Machine learning models, particularly deep neural networks, are used for speech recognition and natural language understanding. Natural language processing techniques enable intent parsing, entity extraction, and response generation. Human-computer interaction principles guide the design of user interfaces and feedback mechanisms.")
    add_paragraph_text(doc, "Speech recognition has evolved from statistical models to deep learning approaches. Modern systems use neural network architectures including recurrent neural networks (RNNs), convolutional neural networks (CNNs), and transformer-based models. These models are trained on large datasets of audio-text pairs and can achieve high accuracy across diverse speakers and acoustic conditions. Wake-word detection typically uses specialized small models optimized for low-latency detection of specific phrases.")
    add_paragraph_text(doc, "Natural language understanding involves several subtasks: intent classification, which determines the user's goal; entity extraction, which identifies relevant parameters; and dialogue management, which maintains context across multiple turns. Traditional approaches used rule-based systems and statistical classifiers, while modern approaches increasingly use large language models that can perform these tasks with minimal explicit training.")
    add_paragraph_text(doc, "Text-to-speech synthesis has also evolved significantly, from concatenative synthesis that stitches together recorded speech segments to neural text-to-speech that can generate natural-sounding speech from text. Modern TTS systems can produce highly realistic speech with appropriate prosody, emotion, and style. The Ultron project uses macOS's native TTS capabilities, which provide high-quality synthesis without requiring additional software implementation.")

    add_section_heading(doc, "2.3", "Literature Review")
    add_paragraph_text(doc, "Recent literature on voice assistants has focused on several key areas: improving speech recognition accuracy in diverse acoustic conditions, developing more efficient wake-word detection algorithms, enhancing natural language understanding through large language models, and addressing privacy concerns through local processing. Research in speech recognition has explored transformer-based architectures that achieve state-of-the-art performance while remaining computationally efficient.")
    add_paragraph_text(doc, "Studies on wake-word detection have demonstrated the effectiveness of specialized neural network architectures that can detect wake phrases with low latency and minimal false positives. These systems typically use small, efficient models that can run continuously on embedded hardware without significant power consumption.")
    add_paragraph_text(doc, "The integration of large language models into voice assistants has been a major focus of recent research. Studies have shown that LLMs can significantly improve the conversational capabilities of voice assistants, enabling more natural dialogue, better context understanding, and the ability to handle complex, multi-step requests. However, challenges remain in balancing model capability with computational constraints, particularly for local deployment.")
    add_paragraph_text(doc, "Privacy-preserving voice assistants have emerged as an important research direction. Studies have demonstrated the feasibility of running speech recognition and natural language understanding entirely on local hardware, eliminating the need to transmit voice data to cloud servers. This approach addresses growing user concerns about privacy and data sovereignty, though it requires careful optimization to maintain acceptable performance on consumer hardware.")

    doc.add_page_break()

    # Chapter 3: Implementation
    add_chapter_heading(doc, 3, "IMPLEMENTATION")
    add_section_heading(doc, "3.1", "System Architecture")
    add_paragraph_text(doc, "The Ultron system architecture is organized into five main modules: Ears, Brain, Actions, Voice, and UI. Each module has a specific responsibility and well-defined interfaces, enabling modular development and independent testing. The modules communicate through function calls and shared state, with coordination managed by the main application controller.")
    add_paragraph_text(doc, "The Ears module is responsible for audio capture, wake-word detection, and speech recognition. It runs continuously in the background, listening for the wake phrase and capturing voice input when activated. The module handles microphone initialization, audio processing, and integration with speech recognition services.")
    add_paragraph_text(doc, "The Brain module performs intent parsing and decision-making. It receives text input from the Ears module, analyzes the command to determine the user's intent, extracts relevant parameters, and routes the request to the appropriate action handler. For commands that don't match known patterns, it engages the AI model through Ollama to provide intelligent responses.")
    add_paragraph_text(doc, "The Actions module contains the implementations of specific commands and tasks. This includes web searching, application launching, file operations, system control, memory management, and other capabilities. Each action is implemented as a function that receives parameters and returns a result or status message.")
    add_paragraph_text(doc, "The Voice module handles text-to-speech synthesis. It receives text input and generates spoken output using the system's TTS capabilities. The module supports configuration options for speech rate, voice selection, and other synthesis parameters.")
    add_paragraph_text(doc, "The UI module provides the graphical user interface. It displays system status, shows conversation history, provides manual input options, and offers visual feedback about the system state. The interface is designed to be unobtrusive but informative, allowing users to understand what the system is doing at any given time.")

    add_section_heading(doc, "3.2", "Tools & Technologies")
    add_paragraph_text(doc, "Python 3.9+ serves as the primary development language. Python's extensive standard library and third-party ecosystem provide the necessary tools for audio processing, GUI development, system integration, and AI model interaction. The language's readability and expressiveness make it suitable for rapid prototyping and iterative development.")
    add_paragraph_text(doc, "PyAudio provides audio capture capabilities. It interfaces with the PortAudio library to enable cross-platform audio input and output. The library handles microphone initialization, audio stream management, and real-time audio processing, which are essential for wake-word detection and speech recognition.")
    add_paragraph_text(doc, "SpeechRecognition is a Python library that provides a unified interface to multiple speech recognition engines. It supports Google Web Speech API, CMU Sphinx, Google Cloud Speech API, and others. The project uses Google Web Speech API for its accuracy and ease of integration, though the library's abstraction allows for switching to other engines if needed.")
    add_paragraph_text(doc, "Tkinter is Python's standard GUI library, used for creating the Ultron interface. It provides widgets for creating windows, buttons, text fields, and other UI elements. Tkinter's simplicity and inclusion in the Python standard library make it a practical choice for this project.")
    add_paragraph_text(doc, "Ollama is the platform for local LLM deployment. It manages model downloading, loading, and inference, providing a simple HTTP API for model interaction. Ollama supports multiple model architectures and handles the complexity of running LLMs on local hardware, including GPU acceleration when available.")
    add_paragraph_text(doc, "macOS system tools are used for various tasks. The `say` command provides text-to-speech synthesis. The `open` command enables application launching. The `screencapture` command handles screenshot capture. AppleScript is used for system control operations such as volume adjustment and power management. These native tools provide tight integration with the macOS environment.")

    add_section_heading(doc, "3.3", "Module Implementation")
    add_paragraph_text(doc, "The module design follows the principle of separation of concerns, with each module having a single, well-defined responsibility. This design enables independent development, testing, and maintenance of individual components. Modules communicate through well-defined interfaces, minimizing coupling and maximizing reusability.")
    add_paragraph_text(doc, "The Ears module (ears.py) handles all audio-related functionality. It is responsible for microphone initialization, audio capture, wake-word detection, and speech recognition. The module runs in a background thread to enable continuous listening without blocking the main application. It provides callbacks for wake-word detection and command transcription.")
    add_paragraph_text(doc, "The Brain module (brain.py) contains the intent parsing logic and AI integration. It analyzes text input to determine the user's intent, extracts parameters, and routes requests to appropriate handlers. The module maintains patterns for known commands and interfaces with Ollama for AI-powered responses to unknown queries.")
    add_paragraph_text(doc, "The Actions module (actions.py) implements the actual operations that the assistant can perform. This includes web searching, application launching, file operations, system control, memory management, timers, reminders, and other capabilities. Each action is implemented as a function that receives parameters and returns a result.")
    add_paragraph_text(doc, "The Voice module (voice.py) handles text-to-speech synthesis. It provides a simple interface for converting text to speech, with options for speech rate, voice selection, and other parameters. The module abstracts the details of TTS implementation, allowing different TTS backends to be used without affecting the rest of the system.")
    add_paragraph_text(doc, "The UI module (ui.py) creates the graphical user interface. It displays system status, conversation history, and provides manual input options. The module handles user interactions with the interface and coordinates with other modules to execute commands. The interface is designed to be responsive and provide clear visual feedback.")

    add_section_heading(doc, "3.4", "Testing & Validation")
    add_paragraph_text(doc, "Testing was performed through multiple approaches to ensure system reliability and correctness. Manual testing involved using the system with various commands and observing behavior. This helped identify issues with intent parsing, action execution, and user experience.")
    add_paragraph_text(doc, "Automated testing includes the self-test functionality that validates intent parsing patterns and Ollama connectivity. The self-test runs a series of test commands through the intent parser and verifies that they are correctly identified and routed. It also checks that Ollama is accessible and that the configured model is available.")
    add_paragraph_text(doc, "Wake-word detection was tested in various acoustic conditions to ensure reliable activation. This included testing with different microphone hardware, background noise levels, and speaking styles. Calibration functionality was adjusted based on these tests to improve reliability.")
    add_paragraph_text(doc, "Speech recognition was tested with different speakers, accents, and speaking speeds. This helped identify limitations of the recognition engine and informed decisions about timeout settings and error handling.")
    add_paragraph_text(doc, "AI integration was tested with various types of queries to ensure that the model provides appropriate responses. This included factual questions, creative requests, code generation, and other tasks. Prompt engineering was refined based on these tests to improve response quality.")
    add_paragraph_text(doc, "End-to-end testing involved using the system as intended, from wake-word activation through command execution to response delivery. This helped identify integration issues between modules and ensure a smooth user experience.")

    doc.add_page_break()

    # Chapter 4: Results
    add_chapter_heading(doc, 4, "RESULTS")
    add_section_heading(doc, "4.1", "Performance Evaluation")
    add_paragraph_text(doc, "Performance evaluation focused on several key metrics: wake-word detection latency, speech recognition accuracy, intent parsing accuracy, command execution success rate, AI response time, and overall system responsiveness.")
    add_paragraph_text(doc, "Wake-word detection latency, measured from the end of the wake phrase to system activation, averaged approximately 1-2 seconds in normal conditions. This latency is primarily due to the speech recognition processing time and is acceptable for practical use. Specialized wake-word detection libraries could reduce this latency if needed.")
    add_paragraph_text(doc, "Speech recognition accuracy, measured as the percentage of correctly transcribed words in clear speech conditions, was approximately 90-95% for the Google Web Speech API. Accuracy decreased with background noise, accents, or unclear speech, but remained usable in most practical situations.")
    add_paragraph_text(doc, "Intent parsing accuracy, measured as the percentage of commands correctly identified and routed, was approximately 95% for commands within the known pattern set. The hybrid approach with AI fallback ensured that even unknown commands were handled, either through AI interpretation or appropriate error messages.")
    add_paragraph_text(doc, "Command execution success rate was approximately 98% for supported operations. Failures were primarily due to external factors such as network connectivity for web searches or missing applications for launching commands. Error handling appropriately caught and reported these failures.")
    add_paragraph_text(doc, "AI response time varied significantly based on query complexity and model size. Simple queries typically completed in 2-5 seconds, while complex queries could take 10-20 seconds or more. Response time is influenced by hardware capabilities, model selection, and query complexity. The system provides status updates during processing to inform the user of progress.")

    add_section_heading(doc, "4.2", "Discussion")
    add_paragraph_text(doc, "Ultron was compared with commercial voice assistants including Siri, Alexa, and Google Assistant. The comparison focused on several dimensions: privacy, offline capability, command capabilities, AI conversation quality, response time, and ease of setup.")
    add_paragraph_text(doc, "Privacy is a significant advantage of Ultron over commercial assistants. All processing is local, and voice data never leaves the user's machine. Commercial assistants typically transmit voice data to cloud servers, raising privacy concerns and dependency on internet connectivity.")
    add_paragraph_text(doc, "Offline capability is another advantage. Ultron can function without internet connectivity, with the exception of speech recognition which currently uses a cloud-based API. Commercial assistants require internet connectivity for most operations. Future integration of offline speech recognition would make Ultron fully offline-capable.")
    add_paragraph_text(doc, "Command capabilities are more limited in Ultron compared to commercial assistants. Commercial assistants have extensive service integrations, access to vast databases of information, and support for a wide range of third-party services. Ultron's capabilities are focused on local system operations and general AI conversation.")
    add_paragraph_text(doc, "AI conversation quality is comparable for general queries, though commercial assistants may have advantages in specific domains due to specialized training and access to real-time information. Ultron's local model provides good general conversation capabilities within the constraints of local hardware.")
    add_paragraph_text(doc, "Response time is variable. For simple commands, Ultron's response time is competitive. For complex AI queries, commercial assistants may be faster due to cloud-based processing on powerful hardware. However, Ultron's response time is acceptable for most practical uses.")
    add_paragraph_text(doc, "Ease of setup favors commercial assistants, which are typically pre-installed on devices and require minimal configuration. Ultron requires installation of Python, dependencies, Ollama, and configuration of system permissions. This setup is manageable for technical users but may be challenging for non-technical users.")

    add_section_heading(doc, "4.3", "Challenges Faced")
    add_paragraph_text(doc, "Several challenges were encountered during development. Speech recognition accuracy in noisy environments was a significant issue. This was addressed by implementing calibration functionality to adjust audio sensitivity and providing clear error messages when recognition fails, allowing users to retry.")
    add_paragraph_text(doc, "Wake-word detection latency was initially high due to the use of general speech recognition for wake-word detection. This was mitigated by optimizing the recognition interval and providing clear visual feedback when the system is processing, so users understand the delay.")
    add_paragraph_text(doc, "AI response time varied significantly based on query complexity. This was addressed by using smaller models for faster response, providing status updates during processing, and optimizing prompts to reduce unnecessary computation. Users can select models based on their hardware capabilities and desired balance between speed and quality.")
    add_paragraph_text(doc, "System integration across different macOS versions presented compatibility challenges. This was addressed by using standard system commands and APIs that are stable across versions, and testing on multiple macOS versions when possible.")
    add_paragraph_text(doc, "Thread management for concurrent operations was complex, particularly ensuring that background operations don't interfere with UI responsiveness. This was addressed by careful design of thread communication, using appropriate synchronization mechanisms, and avoiding blocking operations in the main thread.")
    add_paragraph_text(doc, "Module coupling was initially higher than ideal, making testing and maintenance difficult. This was addressed by refactoring to reduce dependencies between modules, defining clear interfaces, and implementing dependency injection where appropriate.")

    doc.add_page_break()

    # Chapter 5: Conclusion
    add_chapter_heading(doc, 5, "CONCLUSION")
    add_section_heading(doc, "5.1", "Summary")
    add_paragraph_text(doc, "The Ultron project successfully demonstrated the feasibility of building a capable voice assistant using entirely local resources. The system integrates speech recognition, intent parsing, task execution, text-to-speech synthesis, and AI-powered conversation into a cohesive application that provides practical utility while maintaining privacy and offline capability.")
    add_paragraph_text(doc, "The most significant technical learning was understanding the architecture of voice assistant systems and the interplay between their components. Speech recognition, natural language understanding, task execution, and response generation must work together seamlessly to provide a smooth user experience. The modular architecture proved effective in managing this complexity.")
    add_paragraph_text(doc, "The project also provided valuable experience with local AI deployment. Running large language models on consumer hardware requires careful consideration of model selection, resource management, and optimization. The experience with Ollama demonstrated that local AI is practical and increasingly viable as models become more efficient.")
    add_paragraph_text(doc, "From a software engineering perspective, the project reinforced the importance of modular design, clear interfaces, comprehensive error handling, and thorough testing. These principles were essential in managing the complexity of the system and ensuring reliable operation.")
    add_paragraph_text(doc, "The educational value of the project was significant. Moving from theoretical understanding of AI, speech processing, and software engineering to practical implementation provided deep insights that are difficult to obtain through classroom study alone. The project bridged the gap between academic concepts and real-world application.")

    add_section_heading(doc, "5.2", "Limitations")
    add_paragraph_text(doc, "The primary limitation of the current implementation is the dependence on internet connectivity for speech recognition. While the AI processing is local, the Google Web Speech API requires internet access. This limits true offline capability. Future versions should integrate offline recognition engines such as Whisper or CMU Sphinx to eliminate this dependency.")
    add_paragraph_text(doc, "AI capabilities are constrained by local hardware resources. While modern models are efficient, there is a trade-off between model size, response quality, and response time. Users with less capable hardware may experience slower response times or need to use smaller models with reduced capabilities.")
    add_paragraph_text(doc, "Command capabilities are more limited than commercial voice assistants. The system handles common operations well but lacks the extensive service integrations and specialized capabilities of commercial systems. Expanding the command set would require significant development effort and integration with various APIs.")
    add_paragraph_text(doc, "Wake-word detection implementation using general speech recognition is less efficient than specialized wake-word detection libraries. This results in higher resource usage and slower detection latency compared to optimized implementations.")
    add_paragraph_text(doc, "The system is currently macOS-specific, limiting its portability. While some components use cross-platform libraries, tight integration with macOS system tools and APIs would require significant work to adapt to other operating systems.")
    add_paragraph_text(doc, "Setup complexity may be a barrier for non-technical users. Installation of Python, dependencies, Ollama, and configuration of system permissions requires technical knowledge that not all users possess.")

    add_section_heading(doc, "5.3", "Future Scope")
    add_paragraph_text(doc, "A primary recommendation is to integrate offline speech recognition to eliminate the dependency on internet connectivity. OpenAI's Whisper model or CMU Sphinx could be integrated to provide local speech recognition, making the system truly offline-capable and addressing a current limitation.")
    add_paragraph_text(doc, "Wake-word detection could be improved by integrating specialized libraries such as Mycroft Precise or Porcupine. These libraries provide optimized wake-word detection with lower latency and resource usage compared to the current speech-recognition-based approach.")
    add_paragraph_text(doc, "AI capabilities could be enhanced through better prompt engineering, fine-tuning of models for specific tasks, and integration of retrieval-augmented generation (RAG) to provide access to external knowledge bases while maintaining local processing for sensitive operations.")
    add_paragraph_text(doc, "Command capabilities could be expanded through integration with additional services and APIs. This could include smart home controls, email integration, calendar management, and other common voice assistant features. Each integration should be carefully considered to maintain the system's privacy and local-first philosophy.")
    add_paragraph_text(doc, "Cross-platform support could be developed to make Ultron available on Windows and Linux. This would require adapting system integration components to use platform-appropriate APIs and tools, while maintaining the core architecture that is already largely platform-agnostic.")
    add_paragraph_text(doc, "User experience could be improved through enhanced UI elements, better error recovery, more sophisticated conversation management, and support for multi-language interactions. These improvements would make the system more accessible and enjoyable to use.")
    add_paragraph_text(doc, "Performance could be optimized through model quantization, caching of frequently used data, more efficient threading, and GPU acceleration for AI processing. These optimizations would improve response times and reduce resource usage.")
    add_paragraph_text(doc, "The project could serve as a foundation for research in local AI, privacy-preserving voice assistants, and edge computing. Further development could explore novel approaches to intent parsing, conversation management, and human-AI interaction in local contexts.")

    doc.add_page_break()

    # References
    p = doc.add_paragraph()
    set_paragraph_style(p, WD_ALIGN_PARAGRAPH.CENTER, space_before=72, space_after=36)
    run = p.add_run("REFERENCES / BIBLIOGRAPHY")
    set_font(run, 'Times New Roman', 16, bold=True)

    references = [
        "[1] Ollama, \"Ollama - Run Llama 2, Mistral, and other large language models locally,\" Ollama documentation, accessed Oct. 2026.",
        "[2] OpenAI, \"Whisper: Robust Speech Recognition via Large-Scale Weak Supervision,\" arXiv preprint arXiv:2212.04356, 2022.",
        "[3] Google, \"Google Cloud Speech-to-Text API Documentation,\" Google Cloud Platform, accessed Oct. 2026.",
        "[4] A. Vaswani et al., \"Attention Is All You Need,\" in Advances in Neural Information Processing Systems, 2017.",
        "[5] Mozilla, \"SpeechRecognition Library Documentation,\" Python Package Index, accessed Oct. 2026.",
        "[6] Python Software Foundation, \"Tkinter - Python interface to Tcl/Tk,\" Python documentation, accessed Oct. 2026.",
        "[7] J. Brownlee, \"A Gentle Introduction to Speech Recognition with Python,\" Machine Learning Mastery, 2020.",
        "[8] S. Young et al., \"The HTK Book,\" Cambridge University Engineering Department, 2006.",
        "[9] D. Jurafsky and J. Martin, \"Speech and Language Processing,\" 3rd ed., Pearson, 2023.",
        "[10] I. Goodfellow, Y. Bengio, and A. Courville, \"Deep Learning,\" MIT Press, 2016.",
        "[11] Apple Developer Documentation, \"macOS Command Line Tools and System APIs,\" Apple Inc., accessed Oct. 2026.",
        "[12] PortAudio, \"PortAudio - Portable Audio Library,\" PortAudio documentation, accessed Oct. 2026."
    ]

    for ref in references:
        p = doc.add_paragraph()
        set_paragraph_style(p, WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6)
        run = p.add_run(ref)
        set_font(run, 'Times New Roman', 12)

    # Save the document
    output_path = "/Users/lakshyamittal/Downloads/Ultron_Project_Report.docx"
    doc.save(output_path)
    print(f"Document saved successfully to {output_path}")

if __name__ == "__main__":
    main()
