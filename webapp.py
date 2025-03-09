from flask import Flask, render_template, request, redirect, url_for
import rdflib
from rdflib.plugins.sparql import prepareQuery
import spacy

app = Flask(__name__)


nlp = spacy.load("en_core_web_sm")


g = rdflib.Graph()
g.parse("dbpedia_3.4.owl", format="xml")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')

        # Extraction des mots-clés avec NLP
        doc = nlp(query)
        keywords = [token.text for token in doc if token.is_stop == False and token.is_punct == False]
        
        print(keywords)

        # Construction de la requête SPARQL
        sparql_query = """
        SELECT ?subject ?predicate ?object
        WHERE {{
            ?subject ?predicate ?object .
            FILTER (regex(str(?object), "{0}", "i") || regex(str(?subject), "{1}", "i"))
        }}
        LIMIT 10
        """.format("|".join(keywords), "|".join(keywords))

        q = prepareQuery(sparql_query)
        results = g.query(q)
        
        
        formatted_results = []
        if results:
            print("SPARQL result is not empty")
            print(results)
            # Process the results here
            for row in results:
                uri = str(row[0])  # Extract the URI from the tuple
                title = uri.split("/")[-1]  # Extract the last part of the URI as the title
                url = uri
                snippet = f"Description of {title}"

                result_entry = {"title": title, "url": url, "snippet": snippet}
                formatted_results.append(result_entry)
        else:
            print("SPARQL result is empty")

        return render_template('search.html', results=formatted_results, query=query)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)