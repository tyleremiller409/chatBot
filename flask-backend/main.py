import flask
import nltk

nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle

app = flask.Flask("__main__")

with open("intents.json") as file:
    data = json.load(file)

# if you make changes to your json file, delete the pickle file so that it will preprocess the new information
# and deleted the old model so that the new model will be trained on the new preprocessed information
try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    # comment what is happening here because I know I will forget what I did in the future lol
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    # this line of code is what fixed the closed session runtime error
    model = tflearn.DNN(net)
    # not sure about this batch size value, review later if the outputs are not accurate
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

# pass in the user question in the .route function
def getAnswer(question):
    # print("Start talking with the bot whenever you are ready! (Type quit to stop.)")
    # while True:
    #     inp = input("You: ")
    #     if inp.lower() == "quit":
    #         break

        # not sure why index into the list is necessary
        results = model.predict([bag_of_words(question, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if results[results_index] > 0.5:
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg['responses']

            return random.choice(responses)
        else:
            return "I'm not sure how to answer that. Try asking something else!"



@app.route('/')
def index():
    return flask.render_template("index.html", token="Hello Flask+React")


@app.route('/<string:question>')
def answer(question):
    return getAnswer(question)


app.run(debug=True)

# everything works
