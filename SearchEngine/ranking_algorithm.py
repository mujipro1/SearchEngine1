import os
import nltk
import random
from re import sub
from math import log2
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem.snowball import DutchStemmer

nltk.download('stopwords')

def getFilesInFolder(folder_name):
    fileList = [os.path.join(folder_name, file) for file in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, file))]
    return [file for file in fileList if file.endswith(".txt")]

def removeStopWords(query):
    stopWords = set(stopwords.words('english'))
    words = nltk.word_tokenize(query)
    return [word for word in words if word.casefold() not in stopWords]

def getPages(query, idx_data, rank_data):
    """
    Given a Query, this function will return the ranked list of pages.
    """
    allowedSets = {}
    for data in idx_data:
        if data[0] in query:
            data = data[1:]
            for idx in range(len(data)):
               allowedSets[idx] = True if (data[idx] and allowedSets.get(idx, 1)) else False
    
    outputQueries = [rank_data[idx] for idx, qApp in allowedSets.items() if qApp]
    return sorted(outputQueries, key=lambda x: x[1], reverse=True)


def getDocLength(data_list):
    """
    Given a list of recepten file data, this function will return the lengths of each file.
    """
    docLengths = {}
    for idx in range(1, len(data_list[1])):
        docVector = [dl[idx] for dl in data_list]
        vectorLen = sum([value ** 2 for value in docVector[1:]]) ** 0.5
        docLengths[docVector[0]] = vectorLen
    return docLengths


def getCosineSimilarity(data_list, query):
    """
    Given a query and a data list, this function calculates the cosine similarities between them.
    """
    return {data_list[0][i] : sum([dl[i] for dl in data_list if dl[0] in query])for i in range(1, len(data_list[1]))}


def getAccumulatedWeights(data_list, query):
    """
    Given a query and datalist, this function will return the accumulated weight of the datas.
    """
    docLengths = getDocLength(data_list)
    cosSimilarity = getCosineSimilarity(data_list, query)

    queryLength = len(query) ** 0.5

    accumalatedOutput = [[dl, cosSimilarity[dl]/(docLengths[dl]*queryLength)] for dl in docLengths.keys()]
    return sorted(accumalatedOutput, key= lambda x: x[1], reverse= True)


def getTermIncidences(filename):
    """
    Given the name of the file, this function will return the term incidence matrix
    """
    stemmer = DutchStemmer()

    fileData = open(f'{filename}', "r").read().rstrip()
    fileData.translate(str.maketrans("", "", punctuation))
    fileData = sub(r'[0-9]', " ", fileData)
    fileData = sub("\n+", " ", fileData).lower()

    stemmedWords = [stemmer.stem(w) for w in fileData.split(" ")]
    words = set(stemmedWords)

    return {uw: 1 for uw in words if stemmedWords.count(uw)}, words


def getTermDocumentMatrix(base_directory):
    """
    Given a list of all text files, this function will return a 2D list of term document
    """
    textList = {}
    uniqueWords = set()
    files = getFilesInFolder(base_directory)

    for file in files:
        term_incidence, words = getTermIncidences(file)
        uniqueWords |= words
        textList[file] = term_incidence

    firstRow = [""] + list(textList.keys())

    termDocumentMatrix = [[word] + [texts.get(word, 0) for texts in textList.values()] for word in uniqueWords]
    termDocumentMatrix.insert(0, firstRow)

    return termDocumentMatrix

def getPageRankValues(filename, baseDir):
    """
    Given the name of the file with text links, this function will calculate the values of page rank.
    """
    textLinks = dict()
    file = open(filename, "r")
    
    for text in file.readlines():
        text = text.rstrip()
        engaged_texts = text.split(" ")
        textLinks[engaged_texts[0]] = engaged_texts[1:]

    page_rank_values = {text_file: 1 for text_file in textLinks.keys()}
    pointing_links = {page: [pge for pge in textLinks.keys() if page in textLinks[pge]] for page in textLinks.keys()}

    d = 0.9

    for _ in range(12):
        for text_file in textLinks.keys():
            other_pr = 0
            for pointing_text in pointing_links[text_file]:
                outbound_links = len(textLinks[pointing_text])
                
                other_pr += page_rank_values[pointing_text]/outbound_links

            current_page_rank_value = (1-d) + d * other_pr
            page_rank_values[text_file] = current_page_rank_value

    return ([[text, pg] for text, pg in page_rank_values.items()])


def filterResults(results, query):
    """
    Given result of query, this function will refine those results so they can be fed to gui
    """
    results_refined = []
    count = 1    
    for r in results:
        r_refined = [count, round(float(r[1]), 2), r[0]]
        preview_text = open(f'{r[0]}', "r").read().lower()
        
        wordIndex = preview_text.find(query[0].lower())
        r_refined.append("..." + preview_text[wordIndex-10:wordIndex+15] + "...")
        results_refined.append(r_refined)

        count += 1
        if count > 5: break
    return results_refined


def getBoolPagerank(query):
    """
    Given a query, this algorithm will return the output of the search engine.
    """
    query = removeStopWords(query)

    stemmer = DutchStemmer()
    query = [stemmer.stem(q) for q in query]

    global baseDirectory
    baseDirectory = "texts"
    fileTree(getFilesInFolder(baseDirectory))

    tdm = getTermDocumentMatrix(baseDirectory)
    pgd = getPageRankValues("document_graph.txt", baseDirectory) 
    result_pages = getPages(query, tdm, pgd)
    output = filterResults(result_pages, query)
    return output


def fileTree(fileArr):
    print(fileArr)
    # Write the file names to the output file
    if not os.path.isfile('document_graph.txt'):
        f = open('document_graph.txt', 'w')
        for file in fileArr:
            f.write(file + ' ')
        f.write('\n')
        for i in range(len(fileArr)):
            randomLength = random.randint(1, len(fileArr)-5)
            for file in range(randomLength):
                f.write(fileArr[i] + ' ')
                fileIdx = random.randint(0, len(fileArr)-1)
                f.write(fileArr[fileIdx] + ' ')
            f.write('\n')
        f.close()