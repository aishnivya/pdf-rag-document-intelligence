
import streamlit as st       # Import Streamlit to create the web interface
from pypdf import PdfReader  # Import PdfReader to extract text from PDF files
import os  # Used to access environment variables
from dotenv import load_dotenv  # Loads variables from the .env file
from google import genai  # Google Gemini API

# Load environment variables from the .env file
load_dotenv()

# Read the Gemini API key securely
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Create the Gemini API client
gemini_client = genai.Client(api_key=gemini_api_key)

# Check whether the Gemini API key was loaded successfully
if gemini_api_key:
    print("Gemini API key loaded successfully!")
else:
    print("Gemini API key was not found.")

# Import regular expressions for identifying sentence boundaries
import re


# Split PDF text into chunks while keeping sentences together
def split_text_into_chunks(text, chunk_size=1000, overlap=200):

    # Divide the text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Store the final chunks
    chunks = []

    # Store sentences belonging to the current chunk
    current_sentences = []

    # Track the current chunk's character length
    current_length = 0

    # Process each sentence in order
    for sentence in sentences:

        sentence = sentence.strip()

        # Ignore empty sentences
        if not sentence:
            continue

        # Check whether adding this sentence exceeds the chunk size
        if current_sentences and current_length + len(sentence) + 1 > chunk_size:

            # Save the completed chunk
            chunks.append(" ".join(current_sentences))

            # Keep complete sentences from the end as overlap
            overlap_sentences = []
            overlap_length = 0

            for previous_sentence in reversed(current_sentences):

                # Stop when the desired overlap is reached
                if overlap_length + len(previous_sentence) > overlap:
                    break

                overlap_sentences.insert(0, previous_sentence)
                overlap_length += len(previous_sentence) + 1

            # Avoid overlap preventing the next sentence from fitting
            if overlap_length + len(sentence) + 1 > chunk_size:
                overlap_sentences = []
                overlap_length = 0

            # Begin the new chunk with the overlapping sentences
            current_sentences = overlap_sentences
            current_length = overlap_length

        # Add the sentence to the current chunk
        current_sentences.append(sentence)
        current_length += len(sentence) + 1

    # Save the final chunk
    if current_sentences:
        chunks.append(" ".join(current_sentences))

    # Return the completed chunks
    return chunks

# Temporary test to verify sentence-based chunking
if __name__ == "__main__" and False:
    sample_text = (
        "The Mastersizer 3000+ measures particle size using laser diffraction. "
        "Large particles scatter light at small angles. "
        "Small particles scatter light at large angles. "
        "Mie theory is used to calculate particle size."
    )

    test_chunks = split_text_into_chunks(
        sample_text,
        chunk_size=100,
        overlap=20
    )

    for index, chunk in enumerate(test_chunks, start=1):
        print(f"Chunk {index}: {chunk}")


st.set_page_config(
    page_title="AI PDF RAG Assistant",
    page_icon="📄"
)

# Store the latest AI answer and retrieved PDF content
# so they remain available when Streamlit reruns
if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None

if "retrieved_context" not in st.session_state:
    st.session_state.retrieved_context = None

# Remember which PDF is currently being used
if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None

# Display the main title of the application
st.title("📄 AI PDF RAG Assistant")

st.write("Upload a PDF and ask questions about its content.")

# Allow the user to upload a PDF file
uploaded_file = st.file_uploader(
    "Upload your PDF",
    type="pdf"
)

# Check whether the user has uploaded a PDF
if uploaded_file is not None:

    # Create a unique identifier from the uploaded PDF's contents
    import hashlib
    current_pdf_id = hashlib.sha256(uploaded_file.getvalue()).hexdigest()

    # Clear saved results when the uploaded PDF changes
    if st.session_state.pdf_id != current_pdf_id:
        st.session_state.ai_answer = None
        st.session_state.retrieved_context = None
        st.session_state.pdf_id = current_pdf_id

    # Show a success message after the PDF is uploaded
    st.success("PDF uploaded successfully!")

    # Read the uploaded PDF
    pdf_reader = PdfReader(uploaded_file)

    # Create an empty string to store all extracted text
    pdf_text = ""

    # Go through every page in the PDF
    for page in pdf_reader.pages:

        # Extract text from the current page
        page_text = page.extract_text()

        # Add the extracted text only if the page contains readable text
        if page_text:
            pdf_text += page_text + "\n"

    # Show how many pages were found
    st.write(f"Number of pages: {len(pdf_reader.pages)}")

    # Split the extracted PDF text into smaller chunks
    chunks = split_text_into_chunks(pdf_text)

    # Create embeddings for the PDF chunks and cache the result
    # This prevents Gemini from creating the same embeddings every time Streamlit reruns
    @st.cache_data
    def create_chunk_embeddings(chunks):
        embedding_result = gemini_client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunks
        )

        # Extract and return the numerical vectors
        return [
            embedding.values
            for embedding in embedding_result.embeddings
        ]
    # Create embeddings for the PDF chunks using the cached function
    chunk_embeddings = create_chunk_embeddings(chunks)

    # Display the number of embeddings created
    st.write(f"Number of embeddings: {len(chunk_embeddings)}")

    # Display the number of chunks created
    st.write(f"Number of text chunks: {len(chunks)}")

    # Display a preview of the extracted text
    st.subheader("Extracted Text Preview")
    st.write(pdf_text[:2000])

    # Create a question form to prevent unnecessary API requests
    st.subheader("Ask a Question")

    # Streamlit processes the form when the user submits it
    with st.form("question_form"):

        # Allow the user to enter a question about the PDF
        user_question = st.text_input(
            "What would you like to know about this PDF?"
        )

        # Create a button to submit the question
        ask_button = st.form_submit_button("Ask AI")

# Process the question only when the user clicks Ask AI
    if ask_button and user_question:

        # Clear the previous answer when a new question is submitted
        # This prevents displaying an outdated answer if Gemini fails
        st.session_state.ai_answer = None

        # Clear the previous retrieved PDF context
        st.session_state.retrieved_context = None

        # Convert the user's question into a semantic embedding
        question_embedding_result = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=user_question
        )

        # Extract the numerical vector for the question
        question_embedding = question_embedding_result.embeddings[0].values

        # Import cosine similarity to compare semantic embeddings
        from sklearn.metrics.pairwise import cosine_similarity

        # Compare the user's question embedding with all PDF chunk embeddings
        similarities = cosine_similarity(
            [question_embedding],
            chunk_embeddings
        )[0]

        # Find the indices of the 3 most relevant PDF chunks
        # argsort() sorts the indices by similarity score
        # [::-1] reverses the order so the highest scores come first
        # [:3] selects the top 3 indices
        top_chunk_indices = similarities.argsort()[::-1][:3]

        # Retrieve the actual text belonging to the top 3 chunks
        top_chunks = [chunks[index] for index in top_chunk_indices]

        # Combine the retrieved chunks into one context for Gemini
        relevant_context = "\n\n".join(top_chunks)

        # Create a prompt containing the user's question and
        # the relevant information retrieved from the PDF
        prompt = f"""
        Answer the user's question using only the PDF content provided below.

        User question:
        {user_question}

        Relevant PDF content:
        {relevant_context}

        If the answer cannot be found in the provided PDF content,
        say that the information was not found in the PDF.
        """

                # Handle potential errors when requesting an AI-generated answer
        try:
            # Send the retrieved PDF content and question to Gemini
            response = gemini_client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

            # Save Gemini's generated answer in session state
            # This allows the answer to remain visible after Streamlit reruns
            st.session_state.ai_answer = response.text

            # Save the retrieved PDF content used to generate the answer
            st.session_state.retrieved_context = relevant_context

        except Exception as error:
            # Display a friendly message if the AI service fails
            st.error(
                "Unable to generate an AI answer right now. "
                "Please try again later."
            )

            # Display technical details in the terminal for debugging
            print(f"Gemini API error: {error}")

        # Display the saved AI answer even after Streamlit reruns
        if st.session_state.ai_answer is not None:

            # Allow users to inspect the PDF content used for the answer
            with st.expander("View Retrieved PDF Content"):
                st.write(st.session_state.retrieved_context)

            # Display the saved AI-generated answer
            st.subheader("AI Answer")
            st.write(st.session_state.ai_answer)
