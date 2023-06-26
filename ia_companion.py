import streamlit as st
import openai
import trafilatura
from openai.error import Timeout
from openai.error import APIError
from retry import retry
import time
import pyperclip





# Fonction pour afficher la page d'accueil
st.set_page_config(page_title="Votre compagnon IA", 
    page_icon="🐧",
    layout="centered", 
    initial_sidebar_state="expanded", 
    menu_items=None
)

st.header("🐧 Nutnut votre compagnon IA 🐧")

#openai.api_key = "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"

# Définir la clé d'accès API d'OpenAI
openai.api_key = "VOTRE_CLÉ_D'ACCÈS_API"
# Récupérer la clé d'accès API d'OpenAI
api_key = st.sidebar.text_input("Clé d'accès API OpenAI", type="password")


list_system = ["Developpeur", "Rédacteur","Expert SEO","Copywriter","Scientifique","Tree of thoughts"]
bio_system = {list_system[0] : "Tu es un développeur avec 20 années d'expérience. Tu maitrises tous les languages de programation du web. Tu apportes des réponses de qualité et professionnelles. Tu appuis tes sources sur des sites tels que Stack Overflow (https://stackoverflow.com/), GitHub (https://github.com/), Reddit (https://www.reddit.com/r/programming/), Dev.to (https://dev.to/) ou encore  Medium (https://medium.com/). Enfin tu détails toujours précisément toutes les étapes nécessaires",
list_system[1] : "Tu es une rédactrice web avec 20 années d'expérience. Tu es très documentée et aucun sujet ne t'es inconnue. Tu as une vision literaire et tes réponses sont orientées en ce sens. tu fais preuve de générosité et d'empathie, pour autant tu gardes toujorus en tête le sujet de départ et tu y réponds au plus près possible.",
list_system[2] : "Tu es un expert SEO avec 20 années d'expérience. Tu maitrises toutes les techniques avancées de référencement pour positionner ton site sur des mots clés spécifiques. Tu travailles avec une certaine éthique, mais tu n'hésites pas à proposer des solutions dites \"black hat\" si celles-ci semblent pertinentes. Tu as une vision pragmatique et orientée sur le résultat avant tout.",
list_system[3] : "Tu es un copywriter avec 20 années d'expérience. TU excelles dans l'art de la réthorique et tu maitrises les mots avec une grande dextérité. Tu cherches toujours à comprendre quels sont les bénéfices cachés, et tu vas faire en sorte d'apporter des réponses qui sont actionnable et orienté conversion. Ta maitrise du discours est au service de la création de pages de vente ultra efficace ! Tu aimes notamment les deux méthodes suivantes : P.A.S. et A.I.D.A.",
list_system[4] : "Tu es un scientifique avec 20 années d'expérience. Tu ne cherches pas à apporter des réponses qui ferront palisir mais au contraire à apporter des réponses qui sont scientifiquement démontrables et basé unqiuemetn sur des faits et des éléments tangibles. Tu essaies de sources au maximum tes réponses !",
list_system[5] : "Vous êtes trois experts dotés de compétences exceptionnelles en matière de raisonnement logique et répondant en collaboration à une question en utilisant la méthode de l'arbre de pensées (Tree of thoughts). Chaque expert partagera sa réflexion en  détail, en tenant compte des pensées précédentes des autres et en admettant toute erreur. Ils affineront et développeront de manière itérative les idées de chacun, en donnant le crédit là où il est dû. Le processus se poursuit jusqu'à ce qu'une réponse concluante soit trouvée. Organisez toute la réponse dans un format de tableau de démarquage."}

system = st.sidebar.selectbox("Choisissez votre compagnon IA", list_system)
question = st.sidebar.text_area("Votre Question ?")
source = st.sidebar.text_input("Sujet récent ? Insérez ici une source pour aider NutNut")

@st.cache_data(show_spinner=False)
@retry(APIError, tries=9, delay=15, backoff=6)
def call_openai_api(question, sumary, system):
    chat_message = [{"role": "system", "content": f"{system}"},
    {"role": "user", "content": f"Voici une question : {question}\n Inclu dans ta réponse les éléments suivants : {sumary} \nApporte moi la réponse la plus complète possible au format Markdown"}]

    while True:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0.6,
                frequency_penalty=0,
                presence_penalty=0,
                messages= chat_message
            )

            return completion.choices[0].message.content.strip()
        except Timeout as e:
            st.write(f"Erreur {e}. Retrying...")



extract_content = lambda url: trafilatura.extract(trafilatura.fetch_url(url), output_format="html", include_links=True)


if st.sidebar.button("Envoyer"):

    if api_key:
        # Effacer toutes les valeurs de st.session_state et configure la clé api d'open AI
        st.session_state.clear()
        openai.api_key = api_key

        if 'question' not in st.session_state:
            st.session_state['question'] = question

        bio = bio_system[system]
        st.write(f"Votre question :\n")
        st.write(question)

        # Génération de la réponse
        progress_text = "Operation en cours. 🐧 Nutnut génère votre réponse... (cela peut prendre quelques secondes) 🐧"
        my_bar = st.progress(2, text=progress_text)

        if source:
            sumary = extract_content(source)
        else:
            sumary = ""


        reponse = call_openai_api(question, sumary, bio)
        
        if 'reponse' not in st.session_state:
                st.session_state['reponse'] = reponse

        for percent_complete in range(50):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 50, text=progress_text)

        # Affichage de la réponse
        st.subheader("Voici la réponse de nutnut à votre question : ")
        
        with st.expander("", expanded=True):  
            st.markdown(reponse)




# Télécharger la réponse au format Markdown
if 'reponse' in st.session_state:  
    name_file = "nom_de_votre_fichier"
    name_file = st.sidebar.text_input("Nom de votre fichier ?")
    st.sidebar.download_button("Télécharger les données", data=st.session_state["reponse"], file_name=f"{name_file}.md", mime="text/markdown")
    if st.sidebar.button("Copier coller la réponse") :
        nutnut_reponse = st.session_state["reponse"]
        nutnut_question = st.session_state["question"]
        clipboard = f"La question est la suivante :\n {nutnut_question}\n###########\nLa réponse est la suivante : \n{nutnut_reponse}"
        pyperclip.copy(clipboard)
        st.success(f"La réponse a été copiée dans le presse-papier")

if 'reponse' in st.session_state:  
    with st.expander("Historique de la conversation", expanded=False):
        st.markdown(st.session_state["reponse"])