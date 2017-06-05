import re
import subprocess
import json

def GetReviewText(line):
    """
    :param line: Input corresponds to individual review data in JSON format
    :return: Return only the review text field of each review
    """
    reviewData = eval(line)
    return reviewData['reviewText']

def WriteTextToFile(text):
    """
    :param text: Writes the review text into an output file
    :return: N/A
    """
    out = open('temp.txt','w')
    out.write(text)
    out.close()

def RunPOSTagger():
    """
    :return: Runs the Stanford POS tagger on the review text file and returns the tagged text
    """
    output = subprocess.check_output("java -mx300m -classpath stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model models/english-bidirectional-distsim.tagger -textFile temp.txt", shell=True)
    return output

def GetFacets(taggedReview):
    """
    :param taggedReview: Gets the tagged review after being processed by the Stanford POS tagger
    :return: Returns facets for each review. Facets are mainly chosen to be Nouns(NN, NNS) and Proper Nouns (NNP, NNPS)
             in both singular and plural forms. This can be extended to other parts of speech as desired.
    """
    taggedWords = taggedReview.split(" ")
    tags = ['NN', 'NNS', 'NNP', 'NNPS']
    facets = []

    for word in taggedWords:
        for tag in tags:
            if tag in word:
                facets.append(word)

    return facets

def GetFacetSnippet(facets, reviewText):
    """
    :param facets: List of facets extracted for each review
    :param reviewText: The review as obtained from the customer
    :return: A snipped of the review, where the facet word resides.
    """
    out = {}
    reviewWords = reviewText.split(" ")
    for word in facets:
        facet = re.sub('[^a-zA-Z0-9]', '', word)
        facet = facet[0:-3]

        if facet in reviewWords:
            idx = reviewWords.index(facet)
        else:
            continue

        snippet = ""
        for i in range(-4,4):
            # if idx+i< len(reviewWords) and idx+i > 0 and reviewWords[idx+i]:
            if idx + i < len(reviewWords) and idx + i > 0:
                snippet += reviewWords[idx+i] + " "

        out[facet] = snippet

    return out

def ExtractFacets(reviewText):
    """
    Extracts facets from the text fo the review and returns a dictionary of (facet: review snippet)
    :param reviewText: Text of customer review
    :return: dictionary of (facet: review snippet)
    """
    WriteTextToFile(reviewText)
    taggedReview = RunPOSTagger()
    facets = GetFacets(taggedReview)
    outputEntry = GetFacetSnippet(facets, reviewText)

    return outputEntry



def main():
    inputFile = open('reviews_Musical_Instruments_5.json','r')
    outputFile = open('output.json', 'w')

    for line in inputFile:
        reviewText = GetReviewText(line)
        outputEntry = ExtractFacets(reviewText)
        json.dump(outputEntry, outputFile)
        outputFile.write('\n')

    inputFile.close()
    outputFile.close()


if __name__ == "__main__":
    main()