from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Input, LSTM, Dense, Embedding, Concatenate, Dropout, Masking, Bidirectional
from keras.models import Model
from keras.layers.normalization import BatchNormalization
#from keras.utils import to_categorical
from gensim.models import word2vec
#from sklearn.model_selection import train_test_split

import numpy as np
import os
import random
num_lstm1 = 64
num_lstm2 = 32
num_lstm3 = 32
num_lstm4 = 32
num_dense = 64
rate_drop_lstm = 0.1
rate_drop_dense = 0.1
MAX_SEQUENCE_LENGTH = 300
EMBEDDING_DIM = 50
split_number = 48000
data = []
label = []
test_data = []
test_label = []
path = "newslices/"
testpath = "testslices/"
for root, _, files in os.walk(path):
    for name in files:
        f = open(os.path.join(root, name), encoding="utf-8")
        tmp = f.read()
        data.append(tmp)
        label.append(int(name[-5]))
print("start tokenizer")
#tokenizer = Tokenizer(char_level=False,split=" ")
#tokenizer.fit_on_texts(data)
#sequences = tokenizer.texts_to_sequences(data)
#word_index = tokenizer.word_index
sequences = []
test_sequences = []
#dictionary
word_index = {}
dict_index = 1
#establish the dictionary
print("length of data",len(data))
print(data[0][0:4])
print(data[0],'\n',data[1])
print(type(data[0][0:4]))

for i in range(len(data)):
    word_start_index = 0
    for j in range(len(data[i])):
        if ((data[i][j] == ' ' or data[i][j] == '\n' or data[i][j] == '\t') and (j != word_start_index)):
            temp_word = data[i][word_start_index:j]
            word_start_index = j+1
            if (temp_word not in word_index):
                word_index[temp_word] = dict_index
                dict_index += 1
        elif ((data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (data[i][j] in '0123456789')or data[i][j] == '_'):
            word_start_index = word_start_index
        elif (j == len(data[i])-1 and ((data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (data[i][j] in '0123456789') or data[i][j] == '_')):
            temp_word = data[i][word_start_index:j+1]
            word_start_index = j+1
            if (temp_word not in word_index):
                word_index[temp_word] = dict_index
                dict_index += 1
        elif (data[i][j] in '!"#$%&()*+,-./:;<=>?@[\]^`{|}~'):
            if j>word_start_index:
                temp_word = data[i][word_start_index:j]
                if (temp_word not in word_index):
                    word_index[temp_word] = dict_index
                    dict_index += 1
            temp_word = data[i][j]
            word_start_index = j+1
            if (temp_word not in word_index):
                word_index[temp_word] = dict_index
                dict_index += 1
        else:
            word_start_index = j+1
#sequences
for i in range(len(data)):
    word_start_index = 0
    one_sequence = []
    for j in range(len(data[i])):
        if ((data[i][j] == ' ' or data[i][j] == '\n' or data[i][j] == '\t') and (j != word_start_index)):
            temp_word = data[i][word_start_index:j]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        elif ((data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (data[i][j] in '0123456789')or data[i][j] == '_'):
            word_start_index = word_start_index
        elif (j == len(data[i])-1 and ((data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (data[i][j] in '0123456789') or data[i][j] == '_')):
            temp_word = data[i][word_start_index:j+1]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        elif (data[i][j] in '!"#$%&()*+,-./:;<=>?@[\]^`{|}~'):
            if j>word_start_index:
                temp_word = data[i][word_start_index:j]
                if (temp_word in word_index):
                    one_sequence.append(word_index[temp_word])
            temp_word = data[i][j]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        else:
            word_start_index = j+1
    sequences.append(one_sequence)

nb_words = len(word_index)+1

print('word_index is:',word_index)
print(sequences[0])
print('Found %s unique tokens.' % len(word_index))



print("start padding")
pad_sequence = []
pad_label = []
for i in range(len(sequences)):
    if len(sequences[i]) > MAX_SEQUENCE_LENGTH:
        continue
    w2v = []
    for j in range(len(sequences[i])):
        w2v.append(sequences[i][j])
    while len(w2v) < MAX_SEQUENCE_LENGTH:
        w2v.append(0)
    pad_sequence.append(w2v)
    pad_label.append(label[i])
print("padding OK")

for i in range(len(pad_sequence)):
    for j in range(len(pad_sequence[i])):
        pad_sequence[i][j] = str(pad_sequence[i][j])
print("start word2vec")
model = word2vec.Word2Vec(pad_sequence, min_count=1, size=EMBEDDING_DIM)
model.save("word.model")

model = word2vec.Word2Vec.load("word.model")
print("creating enbedding index")
embeddings_index = {}
word_vectors = model.wv
for word, vocab_obj in model.wv.vocab.items():
    if int(vocab_obj.index) < nb_words:
        embeddings_index[word] = word_vectors[word]
print("creating embedding matrix")
embedding_matrix = np.zeros((nb_words, EMBEDDING_DIM))
for word, i in word_index.items():
    if i >= nb_words:
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

print("example of sequence after padding",pad_sequence[0])


#test sequence
for root, _, files in os.walk(testpath):
    for name in files:
        f = open(os.path.join(root, name), encoding="utf-8")
        tmp = f.read()
        test_data.append(tmp)
        test_label.append(int(name[-5]))

for i in range(len(test_data)):
    word_start_index = 0
    one_sequence = []
    for j in range(len(test_data[i])):
        if ((test_data[i][j] == ' ' or test_data[i][j] == '\n' or test_data[i][j] == '\t') and (j != word_start_index)):
            temp_word = test_data[i][word_start_index:j]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        elif ((test_data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (test_data[i][j] in '0123456789')or test_data[i][j] == '_'):
            word_start_index = word_start_index
        elif (j == len(test_data[i])-1 and ((test_data[i][j] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') or (test_data[i][j] in '0123456789') or test_data[i][j] == '_')):
            temp_word = test_data[i][word_start_index:j+1]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        elif (test_data[i][j] in '!"#$%&()*+,-./:;<=>?@[\]^`{|}~'):
            if j>word_start_index:
                temp_word = test_data[i][word_start_index:j]
                if (temp_word in word_index):
                    one_sequence.append(word_index[temp_word])
            temp_word = test_data[i][j]
            word_start_index = j+1
            if (temp_word in word_index):
                one_sequence.append(word_index[temp_word])
        else:
            word_start_index = j+1
    test_sequences.append(one_sequence)

print("start padding")
test_pad_sequence = []
test_pad_label = []
for i in range(len(test_sequences)):
    if len(test_sequences[i]) > MAX_SEQUENCE_LENGTH:
        continue
    w2v = []
    for j in range(len(test_sequences[i])):
        w2v.append(test_sequences[i][j])
    while len(w2v) < MAX_SEQUENCE_LENGTH:
        w2v.append(0)
    test_pad_sequence.append(w2v)
    test_pad_label.append(test_label[i])
print("padding OK")
for i in range(len(test_pad_sequence)):
    for j in range(len(test_pad_sequence[i])):
        test_pad_sequence[i][j] = str(test_pad_sequence[i][j])


pos = []
neg = []
print("length of pad_sequence:",len(pad_sequence))
print("length of pad label:",len(pad_label))
for i in range(len(pad_sequence)):
    if pad_label[i] == 0:
        neg.append(pad_sequence[i])
    else:
        pos.append(pad_sequence[i])
print("positive:",len(pos),"negative:",len(neg))
p_sample = random.sample(pos, 10000)
n_sample = random.sample(neg, 10000)
print("creating pairs")
pairs_1 = []
pairs_2 = []
pair_labels = []
for i in range(30000):
    x1 = random.choice(p_sample)
    y1 = random.choice(p_sample)
    pairs_1.append(x1)
    pairs_2.append(y1)
    pair_labels.append(1)

for i in range(30000):
    x1 = random.choice(n_sample)
    y1 = random.choice(p_sample)
    pairs_1.append(x1)
    pairs_2.append(y1)
    pair_labels.append(0)


#for i in range(15000):
#    x1 = random.choice(p_sample)
#    y1 = random.choice(p_sample)
#    pairs_1.append(x1)
#    pairs_2.append(y1)
#    pair_labels.append(1)
#pair_labels = to_categorical(np.asarray(pair_labels))
seed = 4396
np.random.seed(seed)
np.random.shuffle(pairs_1)
np.random.seed(seed)
np.random.shuffle(pairs_2)
np.random.seed(seed)
np.random.shuffle(pair_labels)

#x_train, x_test, y_train, y_test = train_test_split(pairs, pair_labels, test_size=0.1, random_state=0)
x_train_1 = pairs_1[:split_number]
x_train_2 = pairs_2[:split_number]
x_test_1 = pairs_1[split_number:]
x_test_2 = pairs_2[split_number:]
y_train = pair_labels[:split_number]
y_test = pair_labels[split_number:]

x_train_1 = np.array(x_train_1)
x_train_2 = np.array(x_train_2)
y_train = np.array(y_train)
x_test_1 = np.array(x_test_1)
x_test_2 = np.array(x_test_2)
y_test = np.array(y_test)

print(len(x_train_1))
print(len(x_test_1))

#save_path = "pairs.npz"
#np.savez(save_path, x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)

print("creating model")
def get_model():
#    masking_layer = Masking(mask_value=-1, input_shape=(200, 100))
    embedding_layer = Embedding(nb_words,
                                EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=MAX_SEQUENCE_LENGTH,
                                trainable=True)
    first_lstm_layer1 = Bidirectional(LSTM(num_lstm1, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm,return_sequences=True))
    second_lstm_layer1 = Bidirectional(LSTM(num_lstm2, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm))
    first_lstm_layer2 = Bidirectional(LSTM(num_lstm1, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm,return_sequences=True))
    second_lstm_layer2 = Bidirectional(LSTM(num_lstm2, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm))
#    third_lstm_layer = Bidirectional(LSTM(num_lstm3, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm,return_sequences=True))
#    fourth_lstm_layer = Bidirectional(LSTM(num_lstm4, dropout=rate_drop_lstm, recurrent_dropout=rate_drop_lstm))


    input_1 = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
    embedded_sequences_1 = embedding_layer(input_1)
    sequence_1_input = Masking(mask_value=0, input_shape=(MAX_SEQUENCE_LENGTH,EMBEDDING_DIM))(embedded_sequences_1)
    first_y1 = first_lstm_layer1(sequence_1_input)
    y1 = second_lstm_layer1(first_y1)
#    third_y1 = third_lstm_layer(second_y1)
#    y1 = fourth_lstm_layer(third_y1)
#    y1 = Dense(num_lstm4,activation = 'relu')(y1)

    input_2 = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
    embedded_sequences_2 = embedding_layer(input_2)
    sequence_2_input = Masking(mask_value=0, input_shape=(MAX_SEQUENCE_LENGTH,EMBEDDING_DIM))(embedded_sequences_2)
    first_y2 = first_lstm_layer2(sequence_2_input)
    y2 = second_lstm_layer2(first_y2)
#    third_y2 = third_lstm_layer(second_y2)
#    y2 = fourth_lstm_layer(third_y2)
#    y2 = Dense(num_lstm4,activation = 'relu')(y2)

    merged = Concatenate(axis = -1)([y1, y2])
    merged = Dropout(rate_drop_dense)(merged)
    merged = BatchNormalization()(merged)

    merged = Dense(num_dense, activation='relu')(merged)
    merged = Dropout(rate_drop_dense)(merged)
#    merged = BatchNormalization()(merged)
#    merged = Dense(16, activation='relu')(merged)
#    merged = Dropout(rate_drop_dense)(merged)
    merged = BatchNormalization()(merged)
    preds = Dense(1, activation='sigmoid')(merged)

    model = Model(inputs=[input_1, input_2], outputs=preds)
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])

    return model

print(x_train_1.shape)


model = get_model()
model.fit([x_train_1, x_train_2], y_train,
          batch_size=128,
          epochs=15,
          validation_data=([x_test_1,x_test_2], y_test))
model.save('bilstm_model.h5')