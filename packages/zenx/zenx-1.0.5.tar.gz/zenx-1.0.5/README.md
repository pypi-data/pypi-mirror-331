# ZenX: Text Data Optimizer

## Introduction

ZenX is an advanced optimizer designed to enhance text data processing with efficiency, balance, and innovation. Inspired by the principles of Zen, it achieves peak performance with minimal effort, while the 'X' signifies acceleration, transformation, and cutting-edge capabilities. ZenX streamlines text processing workflows, making them more efficient, accurate, and adaptable to various applications.

## Installation

To install ZenX, run the following command:

```bash
pip install zenx
```

## Example Usage

You can use ZenX in your text optimization workflows as shown below:

```python
import tensorflow as tf
from loglu import LogLU
from zenx import ZenX  # ZenX Text Optimizer

# Define an RNN model
model = tf.keras.models.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=128, input_length=100),
    tf.keras.layers.SimpleRNN(128, activation=LogLU()),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model with ZenX optimizer
model.compile(
    optimizer=ZenX(
        learning_rate=0.001,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-7
    ),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
model.summary()
```

## Feedback & Contributions

If you have feedback or would like to contribute, please feel free to open an issue or contribute on GitHub.

Contact: Email: poorni.m0405@gmail.com, rishichaitanya888@gmail.com

Company: XenReZ ([www.xenrez.co.in](https://xenrez.co.in/))
For collaborations, reach out to us at xenrez.ai@gmail.com.


## License

ZenX is released under the [Apache License 2.0](https://github.com/Rishichaitanya-Nalluri/ZenX/blob/main/LICENSE).

