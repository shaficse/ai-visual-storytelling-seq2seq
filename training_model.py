from keras.layers import LSTM, GRU, CuDNNGRU
from keras.optimizers import *
from keras.callbacks import ModelCheckpoint, CSVLogger
import numpy as np
import h5py
import json
import time
import datetime
from model_data_generator import ModelDataGenerator
from seq2seqbuilder import Seq2SeqBuilder

vocab_json = json.load(open('./dataset/vist2017_vocabulary.json'))
train_dataset = h5py.File('new_train_file.hdf5', 'r')
valid_dataset = h5py.File('new_valid_file.hdf5', 'r')
train_generator = ModelDataGenerator(train_dataset, vocab_json, 64)
valid_generator = ModelDataGenerator(valid_dataset, vocab_json, 64)
words_to_idx = vocab_json['words_to_idx']

batch_size = 13
epochs = 1  # Number of epochs to train for.
latent_dim = 1024  # Latent dimensionality of the encoding space.
word_embedding_size = 300  # Size of the word embedding space.
num_of_stacked_rnn = 1  # Number of Stacked RNN layers

learning_rate = 0.0001
gradient_clip_value = 5.0

num_samples = train_generator.num_samples
num_decoder_tokens = train_generator.number_of_tokens
valid_steps = valid_generator.num_samples / batch_size

ts = time.time()
start_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

# Build model
builder = Seq2SeqBuilder()
model = builder.build_encoder_decoder_model(latent_dim, words_to_idx, word_embedding_size, num_decoder_tokens,
                                            num_of_stacked_rnn, (None, 4096), (22,), cell_type=GRU, masking=True)

optimizer = Adam(lr=learning_rate, clipvalue=gradient_clip_value)
model.compile(optimizer=optimizer, loss='categorical_crossentropy')

# Callbacks
checkpoint_name = start_time + "checkpoit.hdf5"
checkpointer = ModelCheckpoint(filepath='./checkpoints/' + checkpoint_name, verbose=1, save_best_only=True)
csv_logger = CSVLogger("./loss_logs/" + start_time + ".csv", separator=',', append=False)

# Start training
model.fit_generator(train_generator.multiple_samples_per_story_generator(), steps_per_epoch=num_samples / batch_size,
                    epochs=epochs,
                    validation_data=valid_generator.multiple_samples_per_story_generator(),
                    validation_steps=valid_steps, callbacks=[checkpointer, csv_logger])
ts = time.time()

end_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

model.save('./trained_models/' + str(start_time) + "-" + str(end_time) + ':image_to_text_gru.h5')