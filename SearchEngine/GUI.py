from ranking_algorithm import getBoolPagerank
from flask import Flask, redirect, url_for, request

'''
To view the program's htmlCode, launch the GUI file and access the "search_engine.html" file
(included in the downloaded folder) in your browser. This will display the htmlCode.
Additionally, we have incorporated two extensions. The first allows for an unlimited number
of text documents to be taken from a designated directory; new documents can be added by placing
them in the "texts" directory. The second extension involves implementing text stemming 
during preprocessing.
'''

app = Flask(__name__)


@app.route('/success/<name>', methods=['POST', 'GET'])
def renderPage(name):

    results_bool = getBoolPagerank(name)

    #To put a new query in
    htmlCode = ""
    htmlCode += ''''
        <div id="container">
            <div class="form">
                <h1><strong>Search Engine</strong></h1>
                <form action="/app" method="POST">
                    <p>Enter Query:</p>
                    <p><input type = "text" name = "nm" />  </p>
                    <p><input id="search" type = "submit" value = "search!" /></p>
                </form>
            </div>
        </div>
    '''
    #css for the pages
    htmlCode += '<link rel="stylesheet" href="' + url_for('static', filename='style1.css') + '">'
    
    #This wil show the results on the page
    htmlCode += '<div">'
    htmlCode += '<table>'
    if (len(results_bool) == 0):
        htmlCode += "<tr><th><h3>No results found.</h3></th></tr>"
    else:
        htmlCode += '''<tr>
            <th><h2>Result: Boolean + PageRank</h2></th>
            </tr><tr><td>'''
        for rb in results_bool:
            htmlCode += "<p><b>Position:</b>" + str(rb[0]) + " | "
            htmlCode += "<b>Document:</b>" + rb[2] + " | "
            htmlCode += "<b>Score:</b>" + str(rb[1]) 
            htmlCode += f'<br><span class="text">{rb[3]}</span></p>'
            htmlCode += "<hr>"
    htmlCode += '</td></table>'

    if request.method == 'POST':
        user_ = request.form['nm']
        return redirect(url_for('renderPage', name=user_))
    return htmlCode

@app.route('/app', methods=['POST', 'GET'])
def runApp():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('renderPage', name=user))
    else:
        user = request.args.get('nm')
        return redirect(url_for('renderPage', name=user))


if __name__ == '__main__':
	app.run(debug=True)
