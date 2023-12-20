import tensorflow as tf
import pandas as pd
# Setup plotting
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

# Todo: fazer menu para repetir treinamento e para escolher dataset
treinamento = 1
# while(treinamento != 0):
# name_df = input("diga o nome do csv:")
name_df = "combined-csv-files.csv"
emgSamples =  pd.read_csv(name_df,index_col=0)
X = emgSamples.copy()
y = X.pop('gesture')
# X_scaled = scaler.fit_transform(X)
# print(X_scaled)

# print(X)
X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.75)

print(X_train.shape, X_valid.shape)
print(y)

# label_mapping = {'A':0, 'B':1, 'C':2,'D':3, 'E':4}

input_shape = (X.shape[1],)
print(input_shape)

type(X_train)
print(X_train.shape)



# RNN ***********************************************
inputs = tf.keras.Input(shape=(X_train.shape[1],))
expand_dims = tf.expand_dims(inputs, axis=2)
gru = tf.keras.layers.GRU(256, return_sequences=True)(expand_dims)
flatten = tf.keras.layers.Flatten()(gru)
outputs = tf.keras.layers.Dense(4, activation='softmax')(flatten)
model = tf.keras.Model(inputs=inputs, outputs=outputs)
print(model.summary())


# Normal NN **************************
# model = keras.Sequential([
#     # the hidden ReLU layers
#     layers.BatchNormalization( input_shape= input_shape),
#     layers.Dense(800, activation='relu'),
#     layers.Dense(128, activation='relu'),
#     # layers.Dense(units=512, activation='relu'),
#     # the linear output layer 
#     layers.Dense(5, activation= "softmax"),
# ])

# Model compile************************
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=["accuracy"]
)

model.fit(X_train, y_train, epochs= 40)

model_acc = model.evaluate(X_valid, y_valid, verbose=0)[1]
print("Test Accuracy: {:.3f}%".format(model_acc * 100))
# treinamento = input("continuar treinando?")

model.save('gesturePredictor_RNN.model')
class_names = ['Relaxed','Fist','Spock','Pointing']

prediction = model.predict(X_valid)

for i in range(0,10):
    y_v_array = np.array(y_valid);
    print("Previsão: " + class_names[np.argmax(prediction[i])] + "  Gesto efetuado: " + class_names[int(y_v_array[i])])

