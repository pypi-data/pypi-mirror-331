![sugarpy](img/logo.png)

# <div align="center">sugarpy</div>

A library, API and web app for using NLP to perform language sample analysis using the [SUGAR](https://www.sugarlanguage.org/) framework. This is primarily meant as a tool for Speech Language Pathologists (SLPs) to expedite the often time-consuming process of computing SUGAR metrics by hand. The main mode of use for SLPs is the web application [here](https://languagesamples.app/). Behind the web application is an API hosted in Google Cloud. Documentation for that API is [here](https://sugarpy-mrjuj62msa-uc.a.run.app/docs).

The `sugarpy` python library is the core driver of the tool. It uses classical NLP (`spacy`) to perform rule-based and token based analysis on the input language samples. In the future, LLM support will be added to augment the tool and improve accuracy.

## Install

To install the python library, use pip:
```bash
pip install sugar-python
```

You can also clone this repo and install from source using poetry:
```bash
pip install poetry
poetry install
```

Next you will need to install the default model:
```bash
python -m spacy download en_core_web_lg
```

## Use

The main operation in `sugarpy` is `get_metrics`:

```python
from sugarpy import get_metrics

language_samples = [
  "My last name is Y and my middle name is Z",
  "And you can take this bag off and wear it",
  "But it’s a little small",
  "Yea mine didn’t come with one that matches",
  "It didn’t come with this; it came with these markers"
]

metrics = get_metrics(language_samples)
```
The result is an object with the four SUGAR metrics as attributes: `mlu` (mean length utterance), `cps` (clauses per sentence), `wps` (words per sentence), and `tnw` (total number of words).

One can also check whether the resulting metrics are within established averages. The mean and standard deviation for each score depends on the subject's age, and they are found in `sugarpy/norms.py`. To retrieve them, use `get_norms`:

```python
from sugarpy import get_norms

age_y = 4 #Age in years
age_m = 11 #Age in months
norms = get_norms(age_y,age_m, "mlu") # Returns {'min_age': 108, 'max_age': 131, 'mean_score': 9.61, 'sd': 1.52}
```

The `min_age` and `max_age` are measured in months, and are the age range for which the `mean_score` and `sd` (standard deviation) apply. In the above example, children between the ages of 108 months and 131 months have a mean `mlu` score of 9.61, with a standard deviation of 1.52.

All of this data is taken directly from the SUGAR language [website](https://www.sugarlanguage.org/downloads).

## Configuration

The library is configured to use the spacy model `en_core_web_lg` by default. This is a CPU-performant token classification model. You can substitute a different spacy model, such as a transformer-based one like `en_core_web_trf`, by passing `model=<your_model_name>` to the `get_metrics` function:
```python
from sugarpy import get_metrics

...

metrics = get_metrics(language_samples, model="en_core_web_trf")
```
You will need to ensure that any model you pass has already been installed on your machine.

## License

This project is licensed under the MIT license. Please see [LICENSE](./LICENSE) for details.
