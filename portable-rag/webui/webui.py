from rag.rag_pipeline import RAGPipeline

# for web page
import streamlit as st

# pdf generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

class WebUI:
  def __init__(self, pipeline: RAGPipeline, title: str, instructions: str, placeholder: str = 'Please enter your question'):
    self.pipeline = pipeline
    self.title = title
    self.instructions = instructions
    self.prompt_placeholder = placeholder

  async def rootpage(self):
    """Streamlit interface"""
    st.set_page_config(page_title="PortableRAG, GPT-Lab (TAU)", layout="wide")
    self.funders()
    st.header(self.title)
    st.info(self.instructions)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Loop over past chats
    for idx, chat in enumerate(st.session_state.chat_history):
        with st.container(border=True):
            st.markdown("**Query @ {timestamp}:**".format(timestamp=chat['created']))
            st.markdown("```\n{query}\n```".format(query=chat['query']))
            st.markdown("---")
            st.markdown("**Response ({duration:.2f} seconds):**".format(duration=chat['duration']))
            st.markdown(chat['answer'])
            

    # Handle new question
    if user_input := st.chat_input(self.prompt_placeholder):
        with st.spinner('Retrieving and generating response. Please wait...', show_time=True):
            json = await self.retrieve_and_generate_answer(user_input)
        st.session_state.chat_history.append({
            "query": user_input,
            "answer": json.response, # type: ignore
            "created": json.created_at, # type: ignore
            "duration": json.total_duration / 1000000000.0 # type: ignore
        })
        st.rerun()

    # Let user download full chat
    if st.session_state.chat_history:
        pdf_buffer = await self.create_pdf(st.session_state.chat_history)
        st.download_button('Download Chat History as PDF', data=pdf_buffer, file_name="chat_history.pdf", mime="application/pdf")
    
    self.footer()

  def funders(self):
    """ Header's images for funders and stuff """
    container = st.container(height=80, key="header", border=False)
    col1, col2, col3, col4 = container.columns(4, gap="large", vertical_alignment='center')
    with col1:
      st.image("static/images/FI_Co-fundedbytheEU_RGB_Monochrome.png", width=200)
    with col2:
      st.image("static/images/logo_TAU_fi_violetti_RGB.png", width=200)
    with col3:
      st.image("static/images/SatliVaaka_PNG.png", width=200)
    with col4:
      st.image("static/images/GPT-Lab_logo_2024-08-08.svg", width=35)

  def footer(self):
    """Footer info"""
    st.markdown("""
        <style>
          .st-key-header {
            background-color: #f1f1f1;
          }
          .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            color: #555;
            box-shadow: 0px -1px 5px rgba(0, 0, 0, 0.1);
            z-index: 100;
          }
        </style>
        <div class="footer">
            Temotero, GPT-Lab, Tampere University © 2025
        </div>
        """, unsafe_allow_html=True)

  # Convert chat history to a downloadable PDF
  async def create_pdf(self, chat_history):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_bold = styles["Heading2"]
    elements = [Paragraph('<b>Chat History</b>', style_bold), Spacer(1, 0.3 * inch)]

    for chat in chat_history:
        elements.append(Paragraph('<b>User:</b>', style_bold))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(chat['query'], style_normal))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph('<b>AI:</b>', style_bold))
        elements.append(Spacer(1, 0.1 * inch))
        for line in chat['answer'].split('\n'):
            elements.append(Paragraph(line, style_normal))
            elements.append(Spacer(1, 0.1 * inch))

        if len(elements) > 10:
            elements.append(PageBreak())

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

  # Execute RAG Pipeline
  async def retrieve_and_generate_answer(self, query: str, top_k: int=5):
    retval = await self.pipeline.query(query, top_k)
    
    #answer = generate_answer(context, query)
    #sources = "\n".join([f"[{idx+1}] {fname}" for idx, (fname, _) in enumerate(similar_chunks)])
    return retval#\n\n**Sources:**\n{None}"
