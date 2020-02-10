# Labeling with AI - Backend

A tool that assists human labeling unsupervisedly. Both rule-based approach and clustering are adopted. Considered features include image, text, and positions of the bounding boxes.

The image clustering was implemented but not yet adopted.

It started with a solution to a task in [Microsoft x TSMC Careerhack 2020](https://www.microsoft.com/taiwan/events/tsmc/), and this repo was the backend code and API of the project.

## Getting Started
### Prerequisites
```
python 3.6
flask 1.1.1
pytorch 1.0.2
transformers 2.4.1
numpy>=1.8.2
scipy>=0.13.3
scikit-learn 0.20.0
```

### Installing
```
pip install python flask pytorch transformers numpy scipy sklearn 
```

## Running the tests
### Host the backend
1. Download the dataset from Teams and unzip it
2. Put "LabelingTrainingData" in this directory, so the structure of this repo becomes:
    ```
    +-- labeling-backend
    |   +-- LabelingTrainingData
        |   +-- Input
        |   +-- <Ground Truth Dir>
    |   +-- app.py
    |   +-- ...
    ```
3. Run the backend with `python app.py` ([ngrok](https://ngrok.com/) can be used)

### Get the result
After labeling with the frontend UI, the structure of the directory becomes:
```
+-- labeling-backend
|   +-- LabelingTrainingData
    |   +-- Input
    |   +-- <Ground Truth Dir>
    |   +-- Recommend    (created)
    |   +-- Final        (created)
|   +-- app.py
|   +-- ...
```
The directories in `LabelingTrainingData` are:
1. `Input`: The raw `Input` (the one given). It must be created explicitly in advance.
2. `Recommend`:   The predicted labels. Created automatically.
3. `Final`:       The final labeling results for scoring. Created automatically.

### Evaluate the result
The command returns the score.
```
python evaluate.py LabelingTrainingData/[Ground Truth Dir] LabelingTrainingData/Final
```
