import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

indexName = 'compounds'

# Use environment variables for sensitive data
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "*nLVGSfCz+3jr1OsIVeA"),
    ca_certs="/Users/judepops/Documents/PathIntegrate/Code/Processing/semantic_search/elasticsearch-8.13.2/config/certs/http_ca.crt"
)

def search(input_keyword):
    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)
    query = {
        "field": "NAME_VECTOR",
        "query_vector": vector_of_input_keyword,
        "k": 2,
        "num_candidates": 10000,
    }
    res = es.knn_search(index=indexName, knn=query, source=['COMPOUND_ID', 'NAME', 'TYPE'])
    return res["hits"]["hits"]

def add_bg_from_local():
    st.markdown(
        f"""
        <style>
        /* Set up the full-screen background image */
        .stApp {{
            background-image: url("data:image/jpeg;base64,{img_to_base64('graphene.png')}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Overlay a white block over the background */
        .stApp > .main > div:first-child {{
            background-color: white;
            width: calc(100% - 4rem); /* Adjust the width as needed */
            margin: 2rem;
            padding: 2rem;
            border-radius: 0.5rem;
            position: relative;
            z-index: 1;
        }}

        /* Adjust the width of Streamlit components to match the white block */
        .stTextInput, .stButton, .stExpander, .stMarkdown {{
            width: calc(100% - 4rem); /* Adjust this width to match the parent block */
            margin-left: auto;
            margin-right: auto;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

def img_to_base64(img_path):
    import base64
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

    

def main():
    add_bg_from_local()
    st.title("Search for Compound ChEBI ID!")

    st.write("This is an online tool to infer the ChEBI ID of a chemical compound using its IUPAC name."
             " The tool will calculate the vector embedding of the IUPAC name and use a pre-trained BERT LLM model to identify"
             " the corresponding ChEBI ID through a semantic search powered by a KNN search and l2 normalisation.")    

    search_query = st.text_input("Enter your search query")
    
    if st.button("Search"):
        if search_query:
            # Initialize the progress bar
            progress_bar = st.progress(0)
            with st.spinner('Searching...'):
                # Update progress bar during search
                progress_bar.progress(50)  # Adjust based on your expected search progress update
                results = search(search_query)
                progress_bar.progress(100)  # Complete the progress bar
                
                st.subheader("Search Results")
                for result in results:
                    with st.expander(f"Compound Match: {result['_source'].get('NAME', 'N/A')}"):
                        chebi_id = result['_source'].get('COMPOUND_ID', 'N/A')
                        id_type = result['_source'].get('TYPE', 'N/A')
                        match_score = result['_score']
                        image_url = f"https://www.ebi.ac.uk/chebi/displayImage.do?defaultImage=true&chebiId={chebi_id}"
                        
                        # Display ChEBI image
                        st.image(image_url, caption=f"ChEBI Image for {chebi_id}")
                        
                        # Display ChEBI ID and link to ChEBI page
                        st.markdown(f"**ChEBI ID**: {chebi_id}")
                        st.markdown(f"**Match Similarity Score**: {'{:.0f}'.format(match_score * 100)}%")
                        st.markdown(f"**Synonym or IUPAC Name?**: {id_type}")

                        ebi_url = f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:{chebi_id}"
                        st.markdown(f"[View on EBI]({ebi_url})")  # Corrected here
                        
                        st.divider()

if __name__ == "__main__":
    main()


