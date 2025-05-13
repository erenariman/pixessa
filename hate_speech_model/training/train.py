import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from hate_speech_model.preprocessing import preprocess_text


def train_traditional_model():
    # Load dataset
    try:
        df = pd.read_csv('hate_speech_model/training/data/labeled_data.csv')

        df = df.rename(columns={
            'tweet': 'text',
            'class': 'label'
        })
        df = df.drop(columns=['Unnamed: 0', 'count', 'hate_speech', 'offensive_language', 'neither'])

        # Handle missing values
        print("\nMissing values before cleaning:")
        print(df.isna().sum())
        df = df.dropna(subset=['text', 'label'])

        # Preprocess text
        df['cleaned_text'] = df['text'].apply(preprocess_text)

        # Convert to binary classification (0 = neither, 1 = hate/offensive)
        df['label'] = df['label'].apply(lambda x: 1 if x in [0, 1] else 0)

        # Split features and labels
        X = df['cleaned_text']
        y = df['label']

        # Handle class imbalance
        print("\nClass distribution:")
        print(y.value_counts())

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )

        # --- Class Balance Check (Before) ---
        print("\nClass Distribution Before Balancing:")
        print(f"Training: {y_train.value_counts().to_dict()}")
        print(f"Test: {y_test.value_counts().to_dict()}")

        # --- Vectorization ---
        vectorizer = TfidfVectorizer(
            preprocessor=preprocess_text,
            max_features=5000,
            ngram_range=(1, 2)
        )
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        # --- SMOTE Application ---
        print("\nApplying SMOTE...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_vec, y_train)

        # --- Class Balance Check (After) ---
        print("\nClass Distribution After Balancing:")
        print(pd.Series(y_train_balanced).value_counts().to_dict())

        # --- Model Training & Evaluation ---
        model = LogisticRegression(class_weight='balanced', max_iter=1000)
        model.fit(X_train_balanced, y_train_balanced)

        # --- Model Evaluation ---
        # Generate predictions
        y_pred = model.predict(X_test_vec)
        y_proba = model.predict_proba(X_test_vec)[:, 1]  # Probability of positive class

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, target_names=['Normal', 'Hate Speech'])
        conf_matrix = confusion_matrix(y_test, y_pred)

        # Calculate ROC-AUC
        from sklearn.metrics import roc_auc_score, roc_curve
        roc_auc = roc_auc_score(y_test, y_proba)
        fpr, tpr, thresholds = roc_curve(y_test, y_proba)

        # Print metrics
        print("\n" + "=" * 50)
        print("Model Evaluation Metrics")
        print("=" * 50)
        print(f"Accuracy: {accuracy:.4f}")
        print(f"ROC-AUC: {roc_auc:.4f}")
        print("\nClassification Report:")
        print(class_report)
        print("\nConfusion Matrix:")
        print(conf_matrix)

        # Plot ROC Curve
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC Curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")

        # Save plots
        import os
        os.makedirs('reports/figures', exist_ok=True)
        plt.savefig('reports/figures/roc_curve.png')
        plt.close()

        # Save textual report
        with open('reports/training_report.txt', 'w') as f:
            f.write(f"Model Evaluation Report\n{'=' * 30}\n")
            f.write(f"Accuracy: {accuracy:.4f}\n")
            f.write(f"ROC-AUC: {roc_auc:.4f}\n\n")
            f.write("Classification Report:\n")
            f.write(class_report)
            f.write("\n\nConfusion Matrix:\n")
            f.write(str(conf_matrix))

        # --- Error Analysis ---
        # Create error analysis dataframe
        error_df = pd.DataFrame({
            'text': X_test,
            'true_label': y_test,
            'pred_label': y_pred,
            'probability': y_proba
        })

        # Identify misclassified examples
        false_positives = error_df[(error_df['true_label'] == 0) & (error_df['pred_label'] == 1)]
        false_negatives = error_df[(error_df['true_label'] == 1) & (error_df['pred_label'] == 0)]

        print("\n" + "=" * 50)
        print("Error Analysis")
        print("=" * 50)
        print(f"False Positives (Normal classified as Hate): {len(false_positives)}")
        print(f"False Negatives (Hate classified as Normal): {len(false_negatives)}")

        # Save error examples
        error_df.to_csv('reports/error_analysis.csv', index=False)

        # Input: new sentence(s) to classify
        new_texts = ["I hate you!", "Have a great day!", "You're such a loser.", "I dont like that nigga.",
                     "fuck you", "fuck that bitch", "why do all indians smell disgusting", "you are retarded"]

        # Preprocess and vectorize
        X_new = vectorizer.transform(new_texts)

        # Predict
        predictions = model.predict(X_new)

        # Optional: get probabilities
        probas = model.predict_proba(X_new)

        # Map numeric labels to class names
        label_map = {0: "Normal", 1: "Hate Speech"}
        results = [(text, label_map[pred], probas[i][pred]) for i, (text, pred) in
                   enumerate(zip(new_texts, predictions))]

        # Print results
        for text, label, confidence in results:
            print(f"Text: '{text}' → Prediction: {label} (Confidence: {confidence:.2f})")

        import joblib
        import os

        # Save trained model and vectorizer
        os.makedirs('hate_speech_model/training/models', exist_ok=True)
        joblib.dump({
            'model': model,
            'vectorizer': vectorizer
        }, 'hate_speech_model/training/models/model.pkl')

        # --- Return Metrics ---
        return {
            'accuracy': accuracy,
            'roc_auc': roc_auc,
            'class_report': class_report,
            'conf_matrix': conf_matrix,
            'false_positives': len(false_positives),
            'false_negatives': len(false_negatives)
        }


    except FileNotFoundError:
        print("Error: Dataset file not found!")
        return None
